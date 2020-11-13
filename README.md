# WaterLytics: A Dashboard for Visualizing, Monitoring and Predicting Water Use 

Our response to the call for code University spot challenge: students vs climate change!

This is a Water use Monitoring and Prediction Platform built using Dash - interactive Python framework developed by [Plotly](https://plot.ly/). Our solution seeks to augment efforts on water sustainability and helps farmers and communities be aware of their water use and become educated with everything climate change and sustainable water use.

We leverage Machine learning technologies such as SVM, XGBoost to predict phenomena like temperature, rainfall, drought and water use quantities by end-users. We also use IBM Watson to build a chatbot to augment climate and water education efforts.

![](data/dashboard.png)

## Getting Started

### Running the app locally

First create a virtual environment with conda or venv inside a temp folder, then activate it.

```
virtualenv venv

# Windows
venv\Scripts\activate
# Or Linux
source venv/bin/activate

or on macos
conda create --name myenv
conda activate myenv

```

Clone the git repo, then install the requirements with pip

```

git clone https://github.com/BadisaMosesane/water_sustainability
cd water_sustainability
pip install -r requirements.txt

```

Run the app

```
cd waterLytics
python app.py

```

## Sofware Used
- Plotly Dash
- Pandas
- Numpy
- IBM Watson Assistant
- TWC API

## Issues
* chatbot redirects: will like to do trigger within the same page 
* Predictions integrations
* Enhance UI


## Contributions

we welcome contributions to this work, to contribute simply do a Pull Request on the [repo](https://github.com/BadisaMosesane/water_sustainability)

## License
This work will be openly published under Apache 2.0

## Authors
- Badisa Mosesane
- Yolanda Kanyama
- Zaheed Gaffor

## Built With

- [Dash](https://dash.plot.ly/) - Main server and interactive components
- [Plotly Python](https://plot.ly/python/) - Used to create the interactive plots

