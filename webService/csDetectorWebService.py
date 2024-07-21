from csDetectorAdapter import CsDetectorAdapter
from flask import jsonify, request, send_file, render_template, url_for, redirect
import flask
import os
import sys
import csv
import json

p = os.path.abspath('.')
sys.path.insert(1, p)
app = flask.Flask(__name__)
app.config['UPLOAD_FOLDER'] = "/"


@app.route('/getSmells', methods=['GET'])
def get_smells():
    needed_graphs = False
    startDate = None
    endDate = None
    date = None

    if 'repo' in request.args:
        repo = str(request.args['repo'])
    else:
        return "Error: No repo field provided. Please specify a repo.", 400

    if 'branch' in request.args:
        branch = str(request.args['branch'])
    else:
        return "Error: No branch field provided. Please specify a branch.", 400

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

    if 'end' in request.args:
        endDate = request.args['end']

    output_path = "out/output_" + user
    try:
        os.makedirs(output_path)
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

    formattedResult, result, config, excep = tool.executeTool(
        repo, branch, pat, startingDate=sd, outputFolder=output_path, endDate=ed)
    print("\n\n\n", formattedResult)

    paths = []
    if needed_graphs:
        paths.append(os.path.join(config.resultsPath, f"commitCentrality_0.pdf"))
        paths.append(os.path.join(config.resultsPath, f"Issues_0.pdf"))
        paths.append(os.path.join(config.resultsPath, f"issuesAndPRsCentrality_0.pdf"))
        paths.append(os.path.join(config.resultsPath, f"PRs_0.pdf"))

    repo_name = extract_repo_name(repo)
    metrics_filename = os.path.join(os.getcwd(), output_path, repo_name, "results", "results_0.csv")
    metrics_dict = {}

    with open(metrics_filename, "r") as csvfile:
        reader = csv.reader(csvfile)

        # Iterate over the rows in the CSV file
        for row in reader:
            # Add the key-value pair to the dictionary
            metrics_dict[row[0]] = row[1]

    r = jsonify({"result": result, "Formatted Result": formattedResult})
    if excep:
        print("\n\nERRORE execp\n", excep)
        response_dict = json.loads(excep)
        error_message = response_dict.get('error')
        code_value = response_dict.get('code')
        print("Error message:", error_message)
        print("Value code:", code_value)
        return excep, code_value
    return r


def extract_repo_name(url: str) -> str:
    # Remove the protocol and split the URL into parts
    parts = url.replace("https://", "").replace("http://","").rstrip("/").split("/")
    # Check if the URL ends with ".git" and remove it if present
    if parts[-1].endswith(".git"):
        parts[-1] = parts[-1][:-4]
    # Join the last two parts and return the result
    return "/".join(parts[-2:])


@app.route('/uploads/<path:filename>')
def download_file(filename):
    fn = os.path.join(os.getcwd(), filename)
    return send_file(fn)


@app.route('/',  methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if all(request.form.values()):
            url = url_for('get_smells') + '?' + '&'.join([f"{key}={value}" for key, value in request.form.items()])
            return redirect(url)
        else:
            return render_template('home.html', message='Fill all the fields!')
    return render_template('home.html')

app.run(host='0.0.0.0', port=5001, threaded=True)
