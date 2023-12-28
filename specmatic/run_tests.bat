


# run against newsletter openapi.yaml directly
C:\openjdk-20.0.2_windows-x64_bin\jdk-20.0.2\bin/java -jar C:\Users\Administrator\Downloads\specmatic.jar test --testBaseURL http://localhost:5010 .\newsletter\src\newsletter-openapi.yaml

# run against newletter.spec
C:\openjdk-20.0.2_windows-x64_bin\jdk-20.0.2\bin/java -jar C:\Users\Administrator\Downloads\specmatic.jar test --testBaseURL http://localhost:5010 .\specmatic\newsletter.spec

# run against  greeting openapi
C:\openjdk-20.0.2_windows-x64_bin\jdk-20.0.2\bin/java -jar C:\Users\Administrator\Downloads\specmatic.jar test --testBaseURL http://localhost:5002 .\greeting\src\greeting-openapi.yaml

# run against users openapi
C:\openjdk-20.0.2_windows-x64_bin\jdk-20.0.2\bin/java -jar C:\Users\Administrator\Downloads\specmatic.jar test --testBaseURL http://localhost:5001 .\users\src\users-openapi.yaml



