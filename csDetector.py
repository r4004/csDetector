from devNetwork import devNetwork
import sys
import os
import cadocsLogger


logger = cadocsLogger.get_cadocs_logger(__name__)

# since the interface of the execution is only command line input, we want something to adapt our web service
# we will have an adapter class that will extend csDetector and parses the local input


class CsDetector:

    def __init__(self):
        pass

    def executeTool(self, argv):
        # formattedResult can be used to print well formatted data in console (if executed from cli)
        # result instead can be used to return the list of community smells acronym if executed from external sources
        # formattedResult, result, config = devNetwork(argv)
        res = devNetwork(argv)
        if res is not None:
            formattedResult, result = res
            return formattedResult, result


if __name__ == "__main__":

    inputData = sys.argv[1:]
    tool = CsDetector()
    res = tool.executeTool(inputData)
    if res is not None:
        formattedResults, results = res
        logger.info(results)
        print(formattedResults)
