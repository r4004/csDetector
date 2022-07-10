from devNetwork import devNetwork
from typing import Sequence
import sys
import os
import cadocsLogger 


logger = cadocsLogger.get_cadocs_logger(__name__)
# since the interface of the execution is only command line input, we want something to adapt our web service
# we will have an adapter class that will extend csDetector and parses the local input

class CsDetector:

    def executeTool(self, argv):
        # formattedResult can be used to print well formatted data in console (if executed from cli)
        # result instead can be used to return the list of community smells acronym if executed from external sources
        formattedResult, result = devNetwork(argv)
        return formattedResult, result


if __name__ == "__main__":

    inputData = sys.argv[1:]
    tool = CsDetector()
    formattedResults, results = tool.executeTool(inputData)
    logger.info(results)
    print(formattedResults)
