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
    date = None
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
    if 'date' in request.args:
        date = request.args['date']
    try:
        os.mkdir("../out/output_"+user)
    except:
        pass

    tool = CsDetectorAdapter()
    if date is not None:
        print(date)
        els = str(date).split("/")
        sd = els[2]+"-"+els[1]+"-"+els[0]
        print(sd)
        formatted_result, result, config = tool.executeTool(
            repo, pat, startingDate=sd, outputFolder="out/output_"+user)
    else:
        formatted_result, result, config = tool.executeTool(
            repo, pat, outputFolder="out/output_"+user)

    paths = []
    if needed_graphs:
        paths.append(os.path.join(
            config.resultsPath, f"commitCentrality_0.pdf"))
        paths.append(os.path.join(config.resultsPath, f"Issues_0.pdf"))
        paths.append(os.path.join(config.resultsPath,
                     f"issuesAndPRsCentrality_0.pdf"))
        paths.append(os.path.join(config.resultsPath, f"PRs_0.pdf"))

    r = jsonify({"result": result, "files": paths})
    return r


@app.route('/uploads/<path:filename>')
def download_file(filename):
    fn = os.path.join(os.getcwd(), filename)
    return send_file(fn)


@app.route('/', methods=['GET'])
def home():
    return "<h1>Hello!</h1><p>To execute csDetector, please try running /getSmells?repo=REPOSITORY_URL&pat=GIT_PAT.</p>"


app.run(port=5001, threaded=True)
