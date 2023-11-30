# General Notes

## Tool Overview

The purpose of this tool is twofold:

1. Contribute to the list of existing community smells that developers need to be aware of in their community.
2. Provide developers with a tool to automatically detect community smells in their project.
 
### The tool can be used in three different ways: 

## 1) Docker installation
### Requirements:

- Docker Desktop

### Process:

1) Login in Docker Desktop with your account or open a terminal and run command:
``` docker login ```

2) To download docker image if you have a Windows or Linux operating system, run command:
``` docker pull acannavale/cs-detector-webservice:latest ```
alternatively, in case you have macOs Apple Silicon operating system, run this command:
``` docker pull acannavale/cs-detector-webservice:macOS ```

3) Run the Docker image in a container with command:
``` docker run -p 5001:5001 <image_name> ```
replace <image_name> with the name of the image on Docker Desktop (it should be ```acannavale/cs-detector-webservice:latest``` or ```acannavale/cs-detector-webservice:macOS```), alternatively you can run: ``` docker images ``` in order to see all your images

4) Now csDetector is running on port 5001, have fun!

### Build Image Locally
1) Clone the repository

2) Open a terminal and build the Docker image with command:
``` docker build -t <image_name> . ```

3) Run the Docker image in a container with command:
``` docker run -p 5001:5001 <image_name> ```
replace <image_name> with the name of the image on Docker Desktop, alternatively you can run: ``` docker images ``` in order to see all your images

4) Now csDetector is running on port 5001, have fun!

## **2) Standalone usage**

### Requirements:

- Windows 10

- Python 3.8.*

- Java 8.0.231 

### Process:

1) Clone the current repository on your system

2) In the repository find the *installation.exe* file which contains the tool ready to run without any installation

3) Run *csDetector.exe* .

4) After the file created *SentiStrenght* folder

5) See the [references](#references) section for *Senti* installation and add these file in the folder

6) Continue for installation complete


## **3) Manual usage**

### **2.1 Requirements**
- Windows 10
- VSCode 1.45.1
- PowerShell 7.0.1
- Python 3.8.3
- Java 8.0.231


### **2.2 Installation**

The tool require some additional modules to be installed that are listed in the *requirements.txt* file and also requires ConvoKit to be installed correctly. See the [references](#references) section for setup instructions..

All required modules **must be installed** prior to running the tool. 




**1) If your system has Powershell**

Run **installModules.ps1** in PowerShell for a quick and simple setup. This will create an embedded **venv** environment and install all the necessary modules with correct versions without polluting the global namespace.

**2) If your system does not has Powershell**

 Inspect **installModules.ps1** and **requirements.txt** files for a manual installation in an environment that does not have PowerShell. Always remember after the creation of the envirnoment to activate it using the proper activation script inside the **.venv/Scripts** folder.




### **2.3 Running**

The tool can be used in two different ways:

### **2.3.1 Running the tool using CLI**

To run the tool you need run **csdetector.py** with the right parameters. Pass the **--help** parameter to view the documentation. For example:
- (-p) for "GitHub PAT (personal access token) used for querying the GitHub API". 
- **Optional**(-g) for "Google Cloud API Key used for authentication with the Perspective API". 
- (-r) for "GitHub repository URL that you want to analyse". 
- (-s) for  "local directory path to the SentiStregth tool" See the [references](#references) section. 
- (-o) for "Local directory path for analysis output".
- **Optional**(-sd) for “The desired date to start analyzing a project  YYYY-MM-DD”.

### **2.3.2 Using a web service call**

To use the tool in this way, you have to run **csDetectorWebService.py** located in the *webservice* folder of the project. To detect the smells on a repository for example, it will only be necessary to open a browser and do a GET request to **http://localhost:5001/getSmells?repo=your_repo_link&pat=your_github_pat**. The response will be in a JSON format where the smells will be indicated using the acronym convention used in [Community Smells Definition](#community-smells-definitions) 

## **3) Optional Configuration**

### **aliasSimilarityMaxDistance (float)**
For documentation on changing this value see:  
https://github.com/luozhouyang/python-string-similarity#metric-longest-common-subsequence  
*Ex: 0.75*

### **Aliases**
It is recommended to generate and massage author aliases prior to analyzing repositories to minimize the number of duplicate users who have historically used multiple emails for their commits skewing the developer network analysis.

To generate author aliases, run **authorAliasExtractor.py** with the right parameters. Pass **--help** for parameter documentation.

## **4) References**
- GitHub GraphQL API Explorer  
https://docs.github.com/en/graphql/overview/explorer

-  The files of sentistrength tool are "SentiStrength_Data.zip & SentiStrength.jar" and available on: 
    http://sentistrength.wlv.ac.uk/jkpop/ 
	 - You need to extrcat the SentiStrength_Data.zip folder.
	 - You need to install Java in your local device to work with SentiStrength.jar file.
	 - (-s) parameter for "local directory path to the folder that contains these two files"

- ConvoKit
  - Setup  
  https://convokit.cornell.edu/documentation/tutorial.html

  - Politeness features and Markers in Convokit  
  https://github.com/CornellNLP/Cornell-Conversational-Analysis-Toolkit/blob/master/examples/politeness-strategies/Politeness%20Marker%20and%20Summarize%20Demo.ipynb


### Community Smells Definitions: 


``` Organizational Silo Effect (OSE)```: This refers to the presence of isolated subgroups, and lack of communication and collaboration between community developers. As a result, this smell cause an extra unforeseen cost to a project by wasted resources (e.g., time), as well as duplication of code.

```Black-cloud Effect (BCE)``` : This reflects an information overload due to lack of structured communications due to limited knowledge sharing opportunities (e.g., collaborations, discussions, daily stand-ups, etc.), as well as a lack of expert members in the project that are able to cover the experience or knowledge gap of a community.

```Prima-donnas Effect (PDE)``` : This smell appears when a team of people is unwilling to respect external changes from other team members due to inefficiently structured collaboration within a community.

```Sharing Villainy (SV)``` : This smell is caused by a lack of high-quality information exchange activities (e.g., face-to-face meetings). The main side effect of this smell limitation is that community members share essential knowledge such as outdated, wrong and unconfirmed information.

```Organizational Skirmish (OS) ```: The OS is caused by a misalignment between different expertise levels and communication channels among development units or individuals involved in the project. The existence of this smell leads often to dropped productivity and affect the project's timeline and cost.

```Solution Defiance (SD)``` : The solution defiance smell occurs when the development community presents different levels of cultural and experience background, and these variances lead to the division of the community into similar subgroups with completely conflicting opinions concerning technical or socio-technical  decisions to be taken. The existence of the SD often leads to unexpected project delays and uncooperative behaviors among the developers.

```Radio Silence (RS)``` : The ratio silence smell occurs when a high formality of regular procedures takes place due to the inefficient structural organization of a community. The RS community smell typically causes changes to be retarded, as well as a valuable time to be lost due to complex and rigid formal procedures.  The main effect of this smell is an unexpected massive delay in the decision-making process due to the required formal actions needed.

```Truck Factor Smell(TFS)``` : The truck factor smell occurs when most of the project information and knowledge are concentrated in one or few developers. The presence of this smell eventually leads to a significant knowledge loss due to the turnover of developers.

```Unhealthy Interaction (UI)``` :  This smell occurs when discussions between developers are slow, light, brief and/or contains poor conversations. It manifests with low developers participation in the project discussions (e.g., pull requests, issues, etc.) having long delays between messages communications.

```Toxic Communication (TC)``` : This smell occurs when communications between developers are subject to toxic conversations and negative sentiments containing unpleasant, anger or even conflicting opinions towards various issues that people discuss. Developers may have negative interpersonal interactions with their peers, which can lead to frustration and stress. These negative interactions may ultimately result in developers abandoning projects.


### Metrics definitions

#### Developer Contributions metrics  

```NoD ```: Number of developers (NoD): the total number of developers who have changed the code in a project.

```NAD``` : Number of Active Days of an author on a project.

```NCD``` : Number of Commits per Developer in a project.

```SDC``` : Standard Deviation of Commits per developer in a project.

```NCD``` : Number of Core Developers.

```PCD``` : Percentage of Core Developers.

```NSD``` : Number of Sponsored Developers.

```PSD``` : Percentage of Sponsored Developers.

```NPR``` : Total number of Pull Requests.

```SAPR``` : Standard deviation of authors per PR.

```ANAPR``` : Average number of authors per PR.

```NI``` : Number of Issues.

```SDAI``` : Standard deviation of authors per issue report.

```ANAI``` : The average number of authors per issue report.

#### Social Network Analysis metrics

```GDC``` : Graph Degree Centrality.

```SDD``` : Standard Deviation of a graph Degree centrality in a project.

```GBC``` : Graph Betweenness Centrality.

```GCC``` : Graph Closeness Centrality.

```ND``` : Network Density.

```CC``` : Graph Closeness centrality

```ND``` : Network Density


#####  Community metrics     

```NC``` : Number of Communities.

```ACC``` : Average of Commits per Community.

```SCC``` : Standard deviation of Commits per Community.

```ADC``` : Average number of Developers per Community.

```SDC``` : Standard deviation of Developers per Community.


####  Geographic Dispersion metrics 

```TZ``` : Number of time zones

```ACZ``` : Average of Commits per time Zone.

```SCZ``` : Standard deviation of Commits per time Zones.

```ADZ``` : Average number of Developers per time Zone.

```SDZ``` : Standard deviation of Developers per time Zones.

####  Formality metrics 

```NR``` : Number of Releases in a project.

```PCR``` : Parentage of Commits per Release.

```FN``` : Formal Network.

```ADPR``` : Average number of days per PR.

```ADI``` : Average number of days per issue report.

####  Truck Number and Community Members metrics 

```BFN``` : Bus Factor Number.

```TFN``` : Global TruckNumber.

```TFC``` : Truck Factor Coverage.

####  Communication metrics

```ANCPR``` : Average number of comments per PR.

```SCPR``` : Standard deviation of commits per PR.

```NCI``` : Number Comments in issues.

```ANCI``` : Average number of comments per issue report.

```SDCI``` : Standard Deviation of Comments Count per issue report.

#### Sentiment Analysis metrics 

```RTCPR```: Ratio of toxic comments in PR discussions.

```RTCI``` : Ratio of toxic comments in issue discussions.

```RPCPR``` : Ratio of polite comments in PR discussions.

```RPCI``` : Ratio of polite comments in issue discussions.

```RINC``` : Ratio of issues with negative sentiments.

```RNSPRC``` : Ratio of negative sentiments in PR comments.

```RAWPR``` : Ratio of anger words in PR discussions.

```RAWI``` : Ratio of anger words in PR discussions.

```ACCL``` : Average Communication Comments Length.
