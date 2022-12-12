import os, logging, sys, subprocess, time
from dbtext import MySQL_DBText, PipeReaderThread
import capturemock
from glob import glob
import webbrowser

def wait_for_file(fn):
    logging.debug(f"Waiting for file {fn} to appear")
    for _ in range(600):
        if os.path.isfile(fn) and os.path.getsize(fn) > 0:
            time.sleep(1) # allow time for flush
            return
        else:
            time.sleep(0.1)
    print("Timed out waiting for action after 1 minute!", file=sys.stderr)


def find_dependencies(source_fn):
    dependencies = []
    dynamic_ports = False
    with open(source_fn) as f:
        for line in f:
            pos = line.find('_URL"')
            if pos != -1:
                startpos = line.rfind('"', 0, pos) + 1
                dependencies.append(line[startpos:pos + 4])
            elif "DYNAMIC_PORTS" in line:
                dynamic_ports = True
    return dependencies, dynamic_ports

def find_service_info():
    info = []
    for varName, serviceDir in os.environ.items():
        if varName.startswith("SVC_"):
            serviceName = varName[4:].lower()        
            sourceFile = os.path.join(serviceDir, "src", serviceName + ".py")
            if os.path.isfile(sourceFile):
                dependencies, dynamic_ports = find_dependencies(sourceFile)
                if dynamic_ports:
                    dbSchema = os.path.join(serviceDir, "schema.sql")
                    if not os.path.isfile(dbSchema):
                        dbSchema = None 
                    info.append((serviceName, sourceFile, dependencies, dbSchema))
    info.sort(key=lambda info: len(info[2]))
    return info

def start_capturemock(client, server, dep_var, testenv, replayDir):
    manager = capturemock.CaptureMockManager()
    recordFile = client + "-" + server + "-mocks.news"
    recordFromUrl = testenv.get(dep_var)
    if recordFromUrl or not replayDir:
        mode = capturemock.RECORD 
        replayFile = None
    else:
        mode = capturemock.REPLAY
        replayFile = os.path.join(replayDir, recordFile)
    environment = os.environ.copy()
    rcFiles = os.getenv("TEXTTEST_CAPTUREMOCK_RCFILES").split(",")
    if manager.startServer(mode, recordFile, replayFile=replayFile, rcFiles=rcFiles,
                        environment=environment, recordFromUrl=recordFromUrl):
        testenv[dep_var] = environment.get("CAPTUREMOCK_SERVER")
        return manager, recordFile
    else:
        return None, None

def replay_for_servers(replayDir, testenv):
    for replayFile in glob(os.path.join(replayDir, "*mocks*")):
        client, server, _ = os.path.basename(replayFile).split("-")
        client_var = client.upper() + "_URL"
        server_var = server.upper() + "_URL"
        if server_var in testenv and client_var not in testenv:
            capturemock.replay_for_server(replayFile=replayFile, recordFile=os.path.basename(replayFile),
                                          serverAddress=testenv.get(server_var))

def run_backend():
    logging.basicConfig(level=logging.DEBUG, filename="fixture.log")
    replayFile = os.getenv("TEXTTEST_CAPTUREMOCK_REPLAY")
    replayDir = os.path.dirname(replayFile) if replayFile else None
    testenv = os.environ.copy()
    testenv["DYNAMIC_PORTS"] = "1"
    pipe_threads, cpmock_managers, databases = [], [], []
    record = capturemock.texttest_is_recording()
    swagger_record_file, swagger_record_url = None, None
    try:
        service_info = find_service_info()
        for i, (service, source, dependencies, schema) in enumerate(service_info):
            if schema:
                dbname = service + "db_" + str(os.getpid())
                testenv[service.upper() + "_DB_NAME"] = dbname
                db = MySQL_DBText(dbname)
                data_dir = os.path.join("mysqldata", service)
                db.create(sqlfile=schema, tables_dir=data_dir)
                databases.append((service, db))
            for dep_var in dependencies:
                dep_svc = dep_var.lower()[:-4]
                cpmock, _ = start_capturemock(service, dep_svc, dep_var, testenv, replayDir)
                if cpmock:
                    cpmock_managers.append(cpmock)
            logging.debug(f"for service {service}, dependencies are {dependencies}")
            do_swagger_record = record and i == len(service_info) - 1
            if do_swagger_record:
                cpmock, swagger_record_file = start_capturemock("client", service, "CAPTUREMOCK_SERVER", testenv, replayDir)
                logging.debug(f"starting record capturemock at {cpmock.serverAddress}")
                cpmock_managers.append(cpmock)
            command = [ sys.executable, source ]
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                       env=testenv)
            pipeThread = PipeReaderThread(process, "Running on", filename=service + "_log.news")
            pipeThread.start()
            url_line = pipeThread.wait_for_text()
            url = url_line.split()[-1]
            logging.debug(f"started {service} service on url {url}")
            if do_swagger_record:
                cpmock_managers[-1].sendServerLocation(url)
                swagger_record_url = url
            testenv[service.upper() + "_URL"] = url
            pipe_threads.append(pipeThread)

        if record:
            webbrowser.open_new(swagger_record_url + "/docs")
            wait_for_file(swagger_record_file)
        else:
            replay_for_servers(replayDir, testenv)
        for service, db in databases:
            db.dumpchanges(table_fn_pattern='db_' + service + '_{type}.news', tables_dir=os.path.join("mysqldata", service))
            if "TEXTTEST_DB_SETUP" in os.environ:
                db.write_data("mysqldata", json_format=True)
    finally:
        logging.debug("stopping all services")
        for pipeThread in pipe_threads:
            pipeThread.terminate()
        for cpmock in cpmock_managers:
            cpmock.terminate()
        for _, db in databases:
            db.drop()    


if __name__ == "__main__":
    #print(find_service_info(r"d:\texttest_repos\newsletter-microservices"))
    run_backend()