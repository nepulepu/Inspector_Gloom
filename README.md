# ML_project

assignment projects for Machine Learning course

### WID3006 Group Assigment - Depression Indicator Chat Bot

TODO:

1. Text Classification

[] Change the labels from suicide/non-suicide to depression/non-depression

[] Preprocess text

[] Feature Extraction - Word Embedding (gloVe / word2Vec)

[] Creating the model

2. Classification using DASS and Demographic Data

This part of the assignment makes use of the public [Depression Anxiety Stress Scales Responses](https://www.kaggle.com/datasets/lucasgreenwell/depression-anxiety-stress-scales-responses) dataset on Kaggle. To work with the notebook, create a the following folder structure, `data/dass_data` where the downloaded and extracted data is placed in the `dass_data` folder.

[] EDA to check for data quality and check for column correlation with the target variable

- Currently checked columns are relatively clean other than the "major" column which requires some cleaning.
- Current correlation test shows that the individual question scoring has high correlation with the severity and demography data shows promise despite having lower correlation.
- The age column has some odd data which needs to be handled.

[] Feature Engineering

- Currently used features are the individual scores for each question and some of the demographical columns.
- "major" column currently has over 5000 unique values even after replacing NaN values with "None". Requires standardization and cleaning.
- Current feature scaling uses the minmax scaler. Need to check whether categorical features need to be scaled/can be scaled differently.

[] Models to Test

- Logistic Regression, SVM, xgboost, decision trees
- Logistic regression seems to perform well on test set, try cross validation and new data to further test generalisation.
