import os
from dotenv import load_dotenv
from csDetector import CsDetector

# this is the adapter class. we can use it to call the adapter from different sources of input
# by inheriting csDetector, we override the method with bad specified interface with a better
# one that will call the superclass method after parsing the given input


# this is the adapter class. we can use it to call the adapter from different sources of input
# by inheriting csDetector, we override the method with bad specified interface with a better
# one that will call the superclass method after parsing the given input

class CsDetectorAdapter(CsDetector):
    def __init__(self):
        super().__init__()

    def executeTool(self, gitRepository, branch, gitPAT, startingDate="null", sentiFolder="./sentiStrenght", outputFolder="./out", endDate="null"):
        args = ["-p", gitPAT, "-r", gitRepository, "-b", branch, "-s", sentiFolder, "-o", outputFolder]
        if startingDate == "null":
            # in this branch we execute the tool normally because no date was provided
            return super().executeTool(args)

        if(startingDate != "null"):
            args.extend(['-sd', startingDate])

        if(endDate != "null"):
            args.extend(['-ed', endDate])
        return super().executeTool(args)


if __name__ == "__main__":
    load_dotenv()
    SECRET_PAT = os.getenv('SECRET_PAT')

    tool = CsDetectorAdapter()
    formattedResult, result, _, _ = tool.executeTool(gitRepository="https://github.com/tensorflow/ranking",
                                                     branch="master",
                                                     gitPAT=SECRET_PAT,
                                                     startingDate=None,
                                                     outputFolder="./out",
                                                     sentiFolder="./sentiStrenght")
    print(result)
    print(formattedResult)
