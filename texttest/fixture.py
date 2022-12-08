import os, logging, sys, subprocess
from dbtext import MySQL_DBText
import capturemock
from glob import glob

def wait_for_url(proc, ready_text):
    ready_bytes = ready_text.encode()
    for _ in range(20):
        msg_bytes = proc.stdout.readline()
        if ready_bytes in msg_bytes:
            return msg_bytes.decode().strip().split()[-1]

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

def find_service_info(root):
    info = []
    for dirName in glob(os.path.join(root, "*", "src")):
        serviceDir = os.path.dirname(dirName)
        serviceName = os.path.basename(serviceDir)
        sourceFile = os.path.join(dirName, serviceName + ".py")
        if os.path.isfile(sourceFile):
            dependencies, dynamic_ports = find_dependencies(sourceFile)
            if dynamic_ports:
                dbSchema = os.path.join(serviceDir, "schema.sql")
                if not os.path.isfile(dbSchema):
                    dbSchema = None 
                info.append((serviceName, sourceFile, dependencies, dbSchema))
    info.sort(key=lambda info: len(info[2]))
    return info

def start_capturemock(service, dep_var, testenv):
    manager = capturemock.CaptureMockManager()
    recordFile = service + "-" + dep_var.lower()[:-4] + "-mocks.news"
    recordFromUrl = testenv.get(dep_var)
    environment = os.environ.copy()
    rcFiles = os.getenv("TEXTTEST_CAPTUREMOCK_RCFILES").split(",")
    manager.startServer(capturemock.RECORD, recordFile, rcFiles=rcFiles,
                        environment=environment, recordFromUrl=recordFromUrl)
    testenv[dep_var] = environment.get("CAPTUREMOCK_SERVER")
    return manager

def run_backend():
    logging.basicConfig(level=logging.INFO)
    
    testenv = os.environ.copy()
    testenv["DYNAMIC_PORTS"] = "1"
    root = os.getenv("TEXTTEST_HOME")
    processes, cpmock_managers, databases = [], [], []
    try:
        for service, source, dependencies, schema in find_service_info(root):
            if schema:
                dbname = service + "db_" + str(os.getpid())
                testenv[service.upper() + "_DB_NAME"] = dbname
                db = MySQL_DBText(dbname)
                db.create(sqlfile=schema)
                databases.append((service, db))
            for dep_var in dependencies:
                cpmock = start_capturemock(service, dep_var, testenv)
                cpmock_managers.append(cpmock)
            logging.info(f"for service {service}, dependencies are {dependencies}")
            command = [ sys.executable, source ]
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                   env=testenv)
            url = wait_for_url(process, "Running on")
            logging.info(f"started {service} service on url {url}")
            testenv[service.upper() + "_URL"] = url
            processes.append(process)

        capturemock.replay_for_server(serverAddress=testenv.get("NEWSLETTER_URL"))
        for service, db in databases:
            if "TEXTTEST_DB_SETUP" in os.environ:
                db.dump_data_directory()
            db.dumpchanges(table_fn_pattern='db_' + service + '_{type}.news')
    finally:
        logging.info("stopping all services")
        for process in processes:
            process.terminate()
        for cpmock in cpmock_managers:
            cpmock.terminate()
        for _, db in databases:
            db.drop()    


if __name__ == "__main__":
    #print(find_service_info(r"d:\texttest_repos\newsletter-microservices"))
    run_backend()