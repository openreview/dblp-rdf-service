##
# You will write me a python program. When writing python, assume that the python version
# is at least 3.11, and use type hints whenever possible.
#
# Write a python context manager that manages a running Apache Jena Fuseki server.
# The context manager should accept the following arguments:
# - an optional file path to the fuseki-server executable, defaulting to 'fuseki-server'
# - an optional argument that specifies the location to store the database files.
#     If the argument is not specified, the fuseki server should use a memory-based database.
#
# Write a set of test cases for the context manager you just created.
# The test cases should do the following at a minimum:
#   - connect to the running database, then run load, update, and query operations
#   - ensure that the server is properly shut down after the tests are run
#
# Modify the context manager in the following way:
#   - When starting the subprocess, stdin and stdout from the fuseki subprocess will be captured and echoed to
#     the stdout of the main process. This will happen in a non-blocking manner, so that it does not
#     stop the execution of the rest of the program

def test_():
    pass
