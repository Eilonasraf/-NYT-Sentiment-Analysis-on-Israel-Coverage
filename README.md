**NYT Sentiment Analysis on Israel Coverage**

**Overview**
This project conducts a sentiment analysis on articles from The New York Times, focusing on the coverage of Israel from September 2023 to January 2024. It aims to identify trends in the portrayal of Israel, discerning whether the coverage leans towards a positive or negative sentiment over time.

**Features**
Automated Data Retrieval: Utilizes the NYT API to systematically fetch articles that mention "Israel," specifically filtering for content related to the "Gaza Strip."
Comprehensive Data Filtering: Processes articles published within the specified timeframe, ensuring a thorough examination of the available data.
Advanced Sentiment Analysis: Employs Python libraries such as TextBlob and spaCy to analyze the sentiment expressed in the article titles, providing insights into the general tone of the coverage.
Data Visualization: Presents the sentiment analysis results through clear and intuitive graphs, illustrating the sentiment trends over the specified period.

**Getting Started**
Prerequisites
Ensure you have Python 3.x installed on your system, along with the following Python libraries:

1. requests
2. pandas
3. matplotlib
4. TextBlob
5. spaCy

You can install these libraries using the following command:
pip install requests pandas matplotlib textblob spacy

**Installation**
Clone the repository to your local machine:
git clone https://github.com/your-username/NYT-sentiment-analysis-israel.git
(Replace your-username with your actual GitHub username)

Navigate to the project directory.

**Configuration**
Obtain an API key from The New York Times Developer Network and set it as an environment variable:

For Windows:
  set NYT_API_KEY=YourNYTAPIKey
For Unix/Linux/macOS:
  export NYT_API_KEY=YourNYTAPIKey

(Note: Environment variables set in this way are temporary and will need to be reset in new terminal sessions. For persistent variables, add these commands to your shell profile file, such as .bashrc or .bash_profile.)

**Usage**
Run the script from the project directory:
  python nyt-sentiment-analysis.py
  
**Contributing**
  Contributions are welcome! If you have suggestions for improving this project, please:

  1. Fork the repository.
  2. Create a new branch for your changes.
  3. Make your changes and test them.
  4. Submit a pull request with a description of the improvements.
   
**License**
This project is licensed under the MIT License. Feel free to use, modify, and distribute the code as you see fit.

