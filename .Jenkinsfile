pipeline {
    agent any

    stages {
        stage('Docker-Compose build') {
            steps {
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
    }
}