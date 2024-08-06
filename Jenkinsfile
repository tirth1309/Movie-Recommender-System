pipeline {
    agent any
    triggers {
        // Schedule the pipeline to run automatically at a specific time using cron syntax
        // For example, this will run the pipeline every day at midnight
        cron('30 19 * * *')
    }
    parameters {
        choice(name: 'DeployService', choices: ['train-model', 'data-generation-service', 'online-evaluation-service', 'prediction-service','cloud-prediction-service'], description: 'Select the service to be deployed')
        choice(name: 'ReTrainModel', choices: ['Yes', 'No'], description: 'Do you want to retrain the model')
        choice(name: 'UploadModel', choices: ['Yes', 'No'], description: 'Do you want to upload the model')
        string(name: 'IMAGE_TAG', defaultValue: 'gcr.io/mlip-westworld/prediction_service_flask:latestv2', description: 'Docker image tag')
    }

    stages {
        stage('Initialization') {
            steps {
                script {
                    sh 'pip install -r requirements.txt'
                }
            }
        }

        stage('Build') {
            steps {
                echo 'This is the build code'
            }
        }

        stage('Test') {
            steps {
                echo 'This is the Test code. Running Unit Tests. Generating Coverage'
                script {
                    sh 'coverage run --omit="/usr/*" -m pytest tests'
                    sh "coverage report"
                    echo "${params.DeployService}"
                }
            }
        }

        // stage('Deploy Service') {
        //     when {
        //         // Run this stage only if the build was triggered manually
        //         expression { params.DeployService == 'MANUALTRIGGER' }
        //     }
        //     steps {
        //         script {
        //             // Prompt for user choice
        //             def userChoice = input(
        //                 id: 'userChoice', 
        //                 message: 'Select the pipeline to run:', 
        //                 parameters: [
        //                     choice(
        //                         name: 'CHOICE', 
        //                         choices: ['data-generation-service', 'online-evaluation-service', 'prediction-service', 'train-model'], 
        //                         description: 'Choose your pipeline'
        //                     )
        //                 ]
        //             )
        //             // Set the choice as an environment variable
        //             env.PIPELINE_CHOICE = userChoice

        //         }
        //     }
        // }

        stage('Train Model') {
            when {
                // Run this stage only if the user chose Option1
                expression { params.DeployService == 'train-model' }
            }
            steps {
                script {
                    if(!currentBuild.rawBuild.getCauses().find().class.toString().contains('GitHubPushCause')){
                        def deploy_path = '/home/team05/Documents/Westworld/Project/deploy'
                        echo 'Training the model'
                        sh "cp project.properties ${deploy_path}/"
                        sh "cp data_generator/generate_new_train_data.py ${deploy_path}/data_generator/generate_new_train_data.py"
                        sh "cp data_generator/process_log_entries.py ${deploy_path}/data_generator/process_log_entries.py"
                        sh "cp data_generator/user_data_generator.py ${deploy_path}/data_generator/user_data_generator.py"
                        sh "cp utils/file_utils.py ${deploy_path}/utils/"
                        sh "cp model_build/train.py ${deploy_path}/model_build/"
                        sh "cp model_build/prepare_data.py ${deploy_path}/model_build/"
                        sh "cp model_build/model.py ${deploy_path}/model_build/"
                        sh "chmod 777 ${deploy_path}/utils/*.py"
                        sh "chmod 777 ${deploy_path}/data_generator/*.py"
                        // def trainModel = input(
                        //     id: 'trainModel', 
                        //     message: 'Do you want to re-train model:?', 
                        //     parameters: [
                        //         choice(
                        //             name: 'CHOICE', 
                        //             choices: ['Yes', 'No'], 
                        //             description: 'Model re-train'
                        //         )
                        //     ]
                        // )
                        if (params.ReTrainModel == 'Yes') {
                            
                            sh "cp ${deploy_path}/data/current/csv/user_data_1.csv data/current/csv/"                       
                            sh "python3 ${deploy_path}/data_generator/generate_new_train_data.py"
                            sh "python3 ${deploy_path}/model_build/train.py --retrain"
                            sh "cp data/current/json/users_m1.json ${deploy_path}/data/current/json/"
                            sh "cp data/current/json/movies_m1.json ${deploy_path}/data/current/json/"
                            sh "cp data/current/csv/user_data_1.csv ${deploy_path}/data/current/csv/"   
                            sh """
                            cd ${deploy_path}/data/current/csv/
                            /home/team05/miniconda3/bin/dvc add user_data_1.csv
                            """
                            if (params.UploadModel == 'Yes') {
                                sh "cp saved_models/previous_best_model.pkl ${deploy_path}/saved_models/"
                                sh "cp saved_models/old_all_movies_list.pkl ${deploy_path}/saved_models/"
                                sh "cp saved_models/old_user_movie_list.pkl ${deploy_path}/saved_models/"
                                sh "cp saved_models/updated_best_model.pkl ${deploy_path}/saved_models/"
                                sh "cp saved_models/updated_all_movies_list.pkl ${deploy_path}/saved_models/"
                                sh "cp saved_models/updated_user_movie_list.pkl ${deploy_path}/saved_models/"
                                sh """
                                cd ${deploy_path}/saved_models/
                                /home/team05/miniconda3/bin/dvc add updated_best_model.pkl
                                """
                            }
                            sh "chmod 777 ${deploy_path}/saved_models/*"
                            sh "chmod 777 ${deploy_path}/data/current/json/*"
                            sh "chmod 777 ${deploy_path}/data/current/csv/*"
                        }
                    }
                }
            }
        }

        stage('Data Generation Service Pipeline') {
            when {
                // Run this stage only if the user chose Option1
                expression { params.DeployService == 'data-generation-service' }
            }
            steps {
                script{
                    def deploy_path = '/home/team05/Documents/Westworld/Project/deploy'
                    echo "Running pipeline for Data Generation Service"
                    sh "cp data_generator/data_generator.py ${deploy_path}/data_generator/"
                    sh "cp data_generator/process_log_entries.py ${deploy_path}/data_generator/"
                    sh "cp data_validation/data_validator.py ${deploy_path}/data_validation/"
                    sh "cp scripts/data_generator.sh ${deploy_path}/scripts/"
                    sh "cp utils/file_utils.py ${deploy_path}/utils/"
                    sh "chmod 777 ${deploy_path}/data_generator/*.py"
                    sh "chmod 777 ${deploy_path}/data_validation/*.py"
                    sh "chmod 777 ${deploy_path}/server/*.py"
                    sh "chmod 777 ${deploy_path}/utils/*.py"
                    sh "chmod 777 ${deploy_path}/scripts/*.sh"
                }
            }
        }
        
        stage('Online Evaluation Service Pipeline') {
            when {
                // Run this stage only if the user chose Option2
                expression { params.DeployService == 'online-evaluation-service' }
            }
            steps {
                // Steps for Option 2
                script{
                    def deploy_path = '/home/team05/Documents/Westworld/Project/deploy'
                    echo "Running pipeline for Online Evaluation Service"
                    sh "cp evaluation/online_evaluation.py ${deploy_path}/evaluation/"
                    sh "cp utils/file_utils.py ${deploy_path}/utils/"
                    sh "cp server/evaluation_server.py ${deploy_path}/server/"
                    sh "cp server/templates/evaluation_dashboard.html ${deploy_path}/server/templates/"
                    sh "cp scripts/evaluation_service.sh ${deploy_path}/scripts/"
                    sh "chmod 777 ${deploy_path}/evaluation/*.py"
                    sh "chmod 777 ${deploy_path}/server/*.py"
                    sh "chmod 777 ${deploy_path}/utils/*.py"
                    sh "chmod 777 ${deploy_path}/scripts/*.sh"
                }
            }
        }
        
        stage('Prediction Service Pipeline') {
            when {
                expression { params.DeployService == 'prediction-service' }
            }
            steps {
                script {
                    echo "Running pipeline for Prediction Service"
                    def deploy_path = '/home/team05/Documents/Westworld/Project/deploy'
                    sh "cp saved_models/updated_best_model.pkl ${deploy_path}/saved_models/"
                    sh "cp saved_models/updated_all_movies_list.pkl ${deploy_path}/saved_models/"
                    sh "cp saved_models/updated_user_movie_list.pkl ${deploy_path}/saved_models/"
                    sh "cp saved_models/svd_v2.pkl ${deploy_path}/saved_models/"
                    sh "cp scripts/prediction_service.sh ${deploy_path}/scripts/"
                    sh "cp server/templates/dashboard.html ${deploy_path}/server/templates/"
                    sh "cp server/server.py ${deploy_path}/server/"
                    sh "cp utils/file_utils.py ${deploy_path}/utils/"
                    sh "chmod 777 ${deploy_path}/server/*.py"
                    sh "chmod 777 ${deploy_path}/saved_models/svd_v2.pkl"
                    sh "chmod 777 ${deploy_path}/utils/*.py"
                    sh "chmod 777 ${deploy_path}/scripts/*.sh"
                }
            }
        }
    stage('Cloud Prediction Service') {
            when {
                // Run this stage only if the user chose Option1
                expression { params.DeployService == 'cloud-prediction-service' }
            }
            steps {
                script{
                    def deploy_path = '/home/team05/Documents/Westworld/Project/deploy'
                    sh "cp prediction-service-deployment.yaml ${deploy_path}/"
                    sh "cp Dockerfile.server ${deploy_path}/"
                    sh "cp prediction-service.yaml ${deploy_path}/"
                    sh "chmod 777 ${deploy_path}/prediction-service.yaml"
                    sh "chmod 777 ${deploy_path}/prediction-service-deployment.yaml"
                    sh "cd ${deploy_path}"
                    sh """
                    export GOOGLE_APPLICATION_CREDENTIALS=\"/home/team05/Documents/Westworld/Project/deploy/mlip-westworld-768e06e9a5e2.json\"
                    docker login -u _json_key --password-stdin https://gcr.io < \$GOOGLE_APPLICATION_CREDENTIALS
                    """
                    sh "docker buildx build -f ${deploy_path}/Dockerfile.server --platform linux/amd64 -t ${params.IMAGE_TAG} --push ."
                    sh """
                    /home/team05/google-cloud-sdk/bin/gcloud --version
                    export GOOGLE_APPLICATION_CREDENTIALS=\"/home/team05/Documents/Westworld/Project/deploy/mlip-westworld-768e06e9a5e2.json\"
                    sed -i 's|{{IMAGE_TAG}}|${params.IMAGE_TAG}|g' ${deploy_path}/prediction-service-deployment.yaml
                    /home/team05/google-cloud-sdk/bin/gcloud auth activate-service-account --key-file=\$GOOGLE_APPLICATION_CREDENTIALS
                    /home/team05/google-cloud-sdk/bin/gcloud container clusters get-credentials westworld-cluster --zone us-east1-b --project mlip-westworld
                    kubectl config get-contexts
                    kubectl config use-context gke_mlip-westworld_us-east1-b_westworld-cluster
                    export PATH=$PATH:/home/team05/google-cloud-sdk/bin
                    /home/team05/google-cloud-sdk/bin/gcloud components update
                    kubectl get pods
                    kubectl apply -f ${deploy_path}/prediction-service-deployment.yaml
                    """
                    // sh """
                    // sed -i 's|{{IMAGE_TAG}}|${params.IMAGE_TAG}|g' ${deploy_path}/prediction-service-deployment.yaml
                    // kubectl config get-contexts
                    // kubectl get pods
                    // kubectl apply -f ${deploy_path}/prediction-service-deployment.yaml         
                    // """
                    sh "kubectl apply -f ${deploy_path}/prediction-service.yaml"
                }
            }
    }
    }
    post {
        always {
            echo "The pipeline has completed"
        }
    }
}
