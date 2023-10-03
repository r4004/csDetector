from csDetectorAdapter import CsDetectorAdapter
from flask import jsonify, request, send_file
import flask
import os
import sys
p = os.path.abspath('.')
sys.path.insert(1, p)
app = flask.Flask(__name__)
app.config['UPLOAD_FOLDER'] = "/"


@app.route('/getSmells', methods=['GET'])
def get_smells():
    needed_graphs = False
    startDate = None
    endDate = None
    if 'repo' in request.args:
        repo = str(request.args['repo'])
    else:
        return "Error: No repo field provided. Please specify a repo.", 400

    if 'pat' in request.args:
        pat = str(request.args['pat'])
    else:
        return "Error: No pat field provided. Please specify a pat.", 400

    if 'user' in request.args:
        user = str(request.args['user'])
    else:
        user = "default"

    if 'graphs' in request.args:
        needed_graphs = bool(request.args['graphs'])

    if 'start' in request.args:
        startDate = request.args['start']
    if 'date' in request.args:
        date = request.args['date']
    try:
        os.mkdir("../out/output_"+user)
    except:
        pass

    if 'end' in request.args:
        endDate = request.args['end']

    try:
        os.mkdir("out/output_"+user)
    except Exception as e:
        pass

    tool = CsDetectorAdapter()
    sd = "null"
    ed = "null"

    if startDate is not None:
        print(startDate)
        sd = startDate
        print(sd)

    if endDate is not None:
        print(endDate)
        els1 = str(endDate).split("/")
        ed = endDate
        print(ed)

    output_path = "out/output_"+user
    formattedResult, result, config = tool.executeTool(
        repo, pat, startingDate=sd, outputFolder=output_path, endDate=ed)

    paths = []
    if needed_graphs:
        paths.append(os.path.join(
            config.resultsPath, f"commitCentrality_0.pdf"))
        paths.append(os.path.join(config.resultsPath, f"Issues_0.pdf"))
        paths.append(os.path.join(config.resultsPath,
                     f"issuesAndPRsCentrality_0.pdf"))
        paths.append(os.path.join(config.resultsPath, f"PRs_0.pdf"))

    repo_name = extract_repo_name(repo)
    metrics_filename = os.path.join(
        os.getcwd(), output_path, repo_name, "results", "results_0.csv")
    metrics_dict = {}

    with open(metrics_filename, "r") as csvfile:
        reader = csv.reader(csvfile)

        # Iterate over the rows in the CSV file
        for row in reader:
            # Add the key-value pair to the dictionary
            metrics_dict[row[0]] = row[1]

    r = jsonify({"result": result, "files": paths, "metrics": metrics_dict})
    return r


def extract_repo_name(url: str) -> str:
    # Remove the protocol and split the URL into parts
    parts = url.replace("https://", "").replace("http://",
                                                "").rstrip("/").split("/")
    # Check if the URL ends with ".git" and remove it if present
    if parts[-1].endswith(".git"):
        parts[-1] = parts[-1][:-4]
    # Join the last two parts and return the result
    return "/".join(parts[-2:])


@app.route('/uploads/<path:filename>')
def download_file(filename):
    fn = os.path.join(os.getcwd(), filename)
    return send_file(fn)


@app.route('/', methods=['GET'])
def home():
    return "<h1>Hello!</h1><p>To execute csDetector, please try running /getSmells?repo=REPOSITORY_URL&pat=GIT_PAT.</p>"


app.run(host='0.0.0.0', port=5001, threaded=True)
