import os, logging, sys, subprocess
from dbtext import MySQL_DBText, PipeReaderThread
import capturemock
from glob import glob

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

def start_capturemock(service, dep_var, testenv, replayDir):
    manager = capturemock.CaptureMockManager()
    recordFile = service + "-" + dep_var.lower()[:-4] + "-mocks.news"
    recordFromUrl = testenv.get(dep_var)
    if recordFromUrl:
        mode = capturemock.RECORD 
        replayFile = None
    else:
        mode = capturemock.REPLAY
        replayFile = os.path.join(replayDir, recordFile)
    environment = os.environ.copy()
    rcFiles = os.getenv("TEXTTEST_CAPTUREMOCK_RCFILES").split(",")
    manager.startServer(mode, recordFile, replayFile=replayFile, rcFiles=rcFiles,
                        environment=environment, recordFromUrl=recordFromUrl)
    testenv[dep_var] = environment.get("CAPTUREMOCK_SERVER")
    return manager

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
    replayDir = os.path.dirname(os.getenv("TEXTTEST_CAPTUREMOCK_REPLAY"))
    testenv = os.environ.copy()
    testenv["DYNAMIC_PORTS"] = "1"
    pipe_threads, cpmock_managers, databases = [], [], []
    try:
        for service, source, dependencies, schema in find_service_info():
            if schema:
                dbname = service + "db_" + str(os.getpid())
                testenv[service.upper() + "_DB_NAME"] = dbname
                db = MySQL_DBText(dbname)
                db.create(sqlfile=schema)
                databases.append((service, db))
            for dep_var in dependencies:
                cpmock = start_capturemock(service, dep_var, testenv, replayDir)
                cpmock_managers.append(cpmock)
            logging.debug(f"for service {service}, dependencies are {dependencies}")
            command = [ sys.executable, source ]
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                       env=testenv)
            pipeThread = PipeReaderThread(process, "Running on", filename=service + "_log.news")
            pipeThread.start()
            url_line = pipeThread.wait_for_text()
            url = url_line.split()[-1]
            logging.debug(f"started {service} service on url {url}")
            testenv[service.upper() + "_URL"] = url
            pipe_threads.append(pipeThread)

        replay_for_servers(replayDir, testenv)
        for service, db in databases:
            if "TEXTTEST_DB_SETUP" in os.environ:
                db.dump_data_directory()
            db.dumpchanges(table_fn_pattern='db_' + service + '_{type}.news')
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