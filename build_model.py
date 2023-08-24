import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import cross_validate
from imblearn.over_sampling import SMOTE
from sklearn.preprocessing import OneHotEncoder
from sklearn.feature_selection import SelectKBest, f_classif
from joblib import dump
import yaml

class EmployeeChurnClassifier:
    def __init__(self, config_path='config.yaml'):
        self.config_path = config_path

    def load_constants(self):
        """
        Load constants from the config file.
        """
        with open(self.config_path, 'r') as yaml_file:
            constants = yaml.safe_load(yaml_file)
            self.CSV_PATH = constants['csv_path']
            self.OVERSAMPLING = constants['oversampling']
            self.SCORING = constants['scoring']
            self.MAX_DEPTH = constants['max_depth']
            self.NUM_FEATURES_CLF = constants['num_features_clf']

    def set_seed(self):
        """
        Set the seed for reproducibility.
        """
        np.random.seed(0)

    def load_dataset(self):
        """
        Load the dataset from the CSV file.
        """
        self.df = pd.read_csv(self.CSV_PATH)
        
    def preprocess_dataset(self):
        """
        Preprocess the dataset.
        """
        # Convert city feature to int
        self.df['city'] = self.df['city'].map(lambda row: int(row.split('_')[1]))
        
        # Define functions for mapping categorical features to integers
        def convert_experience_to_int(row):
            if row is np.nan:
                return '-1'
            elif row == '<1':
                return '0'
            elif row == '>20':
                return '21'
            else:
                return row

        def convert_size_to_int(row):
            if row is np.nan:
                row = -1
            elif '+' in row:
                row = 10000
            elif '/' in row:
                row = 10
            elif '<' in row:
                row = 0
            elif '-' in row:
                row = row.split('-')[0]
            return row

        def convert_last_job_to_int(row):
            if row is np.nan:
                return -1
            elif '>' in row:
                return 4
            elif row == 'never':
                return 0
            else:
                return int(row)

        def convert_ed_level_to_int(row):
            if row is np.nan:
                return -1
            elif row == 'Primary School':
                return 0
            elif row == 'High School':
                return 1
            elif row == 'Graduate':
                return 2
            elif row == 'Masters':
                return 3
            elif row == 'Phd':
                return 4
            else:
                return row
        
        # Apply the conversion functions to respective columns
        self.df['experience'] = self.df['experience'].map(convert_experience_to_int).astype(np.int8)
        self.df['company_size'] = self.df['company_size'].map(convert_size_to_int)
        self.df['last_new_job'] = self.df['last_new_job'].map(convert_last_job_to_int)
        self.df['education_level'] = self.df['education_level'].map(convert_ed_level_to_int)
        
        
    def encode_features(self):
        """
        Encode categorical features.
        """
        
        # Fill NaN values
        self.df = self.df.fillna('not_specified')
        
        enc = OneHotEncoder()
        X_to_encode = self.df[['city', 'gender', 'relevent_experience', 'enrolled_university', 'major_discipline', 'company_type']]
        self.y = self.df.iloc[:, -1]  # Store target variable
        
        X_to_encode = enc.fit_transform(X_to_encode).toarray()
        encoded_df = pd.DataFrame(X_to_encode, columns=enc.get_feature_names_out(enc.feature_names_in_))
        
        non_categorical_cols = ['city_development_index', 'experience', 'company_size', 'last_new_job', 'training_hours', 'education_level']
        self.X_non_categorical = self.df[non_categorical_cols]
        
        self.X_encoded = pd.concat([self.X_non_categorical, encoded_df], axis=1)
        

    def apply_oversampling(self):
        """
        Apply oversampling if configured.
        """
        if self.OVERSAMPLING:
            self.X_encoded, self.y = SMOTE().fit_resample(self.X_encoded, self.y)

    def select_features(self):
        """
        Select the best features using ANOVA.
        """
        feature_selector = SelectKBest(f_classif, k=self.NUM_FEATURES_CLF)
        X_new = feature_selector.fit_transform(self.X_encoded, self.y)
        best_features = feature_selector.get_feature_names_out()
        self.X_final = pd.DataFrame(X_new, columns=best_features)

    def train_classifier(self):
        """
        Train the Decision Tree classifier and save the best model.
        """
        tree = DecisionTreeClassifier(random_state=0, max_depth=self.MAX_DEPTH)
        result = cross_validate(tree, self.X_final, self.y, cv=5, scoring='accuracy', return_estimator=True)
        best_tree = result['estimator'][np.argmax(result['test_score'])]
        self.best_accuracy = np.max(result['test_score']) * 100.0

        self.best_tree = best_tree
        self.dump_classifier()

    def dump_classifier(self):
        """
        Dump the best classifier to a file.
        """
        dump(self.best_tree, 'clf.joblib')
        print(f"Accuracy achieved: {self.best_accuracy:.2f} %")

    def run_classifier_pipeline(self):
        """
        Run the entire classifier pipeline from loading the dataset to training the classifier.
        """
        print("Loading constants...")
        self.load_constants()
        print("Setting seed for reproducibility...")
        self.set_seed()
        print("Loading dataset...")
        self.load_dataset()
        print("Preprocessing dataset...")
        self.preprocess_dataset()
        print("Encoding features...")
        self.encode_features()
        if self.OVERSAMPLING:
            print("Applying oversampling...")
        else:
            print("Oversampling is not applied.")
        self.apply_oversampling()
        print(f"Selecting {self.NUM_FEATURES_CLF} features using ANOVA...")
        self.select_features()
        print("Training the Decision Tree classifier...")
        self.train_classifier()
        print("\nPipeline completed.")

if __name__ == "__main__":
    classifier = EmployeeChurnClassifier()
    print('Start the pipeline:\n')
    classifier.run_classifier_pipeline()
