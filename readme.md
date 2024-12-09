1.Sample dataset.csv is provided for testing whether the system runs successfully.  In practical applications, please replace it with your password file and modify the input module according to the storage format.

2.To protect user privacy,  we are unable to publicly disclose the complete dataset, especially the part that includes real PII. However, you can choose the Kaggle dataset recommended in our paper or the dataset captured.

3.run password_pre.py to get a hash bucket of all passwords.  Run password_decommender.exe to test if the recommender is working properly.

4.You can go to weak_generator-py, Test the sample in strong_generationr.py, PII based password_generationr.py first. If using the online LLM API, please remember to anonymize personal information.

5.Batch generates the entire CSV file in the main. py and LLM will automatically determine the password type and select the appropriate strategy, ultimately obtaining a CSV file that includes honeywords.csv.

6.In shuffle. py, you can choose between traditional shuffle mode or global shuffle mode, which will result in different passwords. csv. Output all candidates to a new password file, and another index file will be saved on the honeywords server.

7.You can use your own API key or a local fine-tuning large model as the base model. The recommended temperature for GPT-4o mini is 0.6, and excessively high temperatures may result in unstable generation or abnormal analysis.

8.If there are too many password entries that need to be processed, you can replace the serial processing mode with parallel processing mode to obtain honeywords faster.

9.The performance of the models used in the comparative experiment is closely related to the password dataset used for training. We used rockyou2024.txt to train them, and you can also train them locally for more complete testing. However, it should be noted that fixed HGT can be very fragile when facing natural entropy style HTT.

10.You can add password generation plugins according to your actual needs, or use a certain expert model as a sub generator to achieve more powerful dynamic defense, rather than just limited to these three generation strategies. Enjoy building your own snooper hunter!

If you have better ideas or dataset requirements, please contact the system developer's email: chenyiren@iie.ac.cn .