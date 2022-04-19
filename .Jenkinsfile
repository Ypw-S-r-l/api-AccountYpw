pipeline {
    agent any

    stages {
        stage('Docker-Compose build') {
            steps {
               echo "No root"
               sh "docker-compose build"
               echo "Exito Build docker"
            }
        }
        stage('Docker-compose create') {
            steps {
                sh "docker-compose create"
            }
        }
        stage('Docker-compose start') {
            steps {
                sh "docker-compose start"
            }
        }
        stage('Image remove, container etc.') {
            steps {
                sh "yes | docker system prune -a"
            }
        }
        

    }
}