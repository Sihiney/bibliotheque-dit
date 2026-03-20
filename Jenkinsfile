// ══════════════════════════════════════════════════════════
//  BIBLIOTHEQUE NUMERIQUE DIT - Pipeline Jenkins CI/CD
//  Ce fichier decrit les etapes automatiques a chaque push
// ══════════════════════════════════════════════════════════

pipeline {

    agent any

    environment {
        PROJECT_NAME = "bibliotheque-dit"
        DOCKER_COMPOSE_FILE = "docker-compose.yml"
    }

    stages {

        stage('Recuperation du code') {
            steps {
                echo 'Recuperation du code depuis GitHub...'
                checkout scm
                echo 'Code recupere avec succes'
            }
        }

        stage('Verification du projet') {
            steps {
                echo 'Verification de la structure du projet...'
                sh '''
                    echo "Structure du projet :"
                    ls -la

                    echo "Verification des Dockerfiles..."
                    test -f service-livres/Dockerfile       && echo "Dockerfile livres OK"
                    test -f service-utilisateurs/Dockerfile && echo "Dockerfile utilisateurs OK"
                    test -f service-emprunts/Dockerfile     && echo "Dockerfile emprunts OK"
                    test -f frontend/Dockerfile             && echo "Dockerfile frontend OK"
                    test -f docker-compose.yml              && echo "docker-compose.yml OK"
                '''
            }
        }

        stage('Build des images Docker') {
            steps {
                echo 'Construction des images Docker...'
                sh 'docker compose -f ${DOCKER_COMPOSE_FILE} build --no-cache'
                echo 'Images construites avec succes'
            }
        }

        stage('Arret de l ancienne version') {
            steps {
                echo 'Arret des anciens conteneurs...'
                sh 'docker compose -f ${DOCKER_COMPOSE_FILE} down --remove-orphans || true'
                echo 'Anciens conteneurs arretes'
            }
        }

        stage('Deploiement') {
            steps {
                echo 'Demarrage des nouveaux conteneurs...'
                sh 'docker compose -f ${DOCKER_COMPOSE_FILE} up -d'
                echo 'Application deployee'
            }
        }

        stage('Verification sante des services') {
            steps {
                echo 'Verification des services...'
                sh '''
                    sleep 15
                    curl -f http://localhost:8001/health && echo "Service Livres OK"       || echo "Service Livres KO"
                    curl -f http://localhost:8002/health && echo "Service Utilisateurs OK" || echo "Service Utilisateurs KO"
                    curl -f http://localhost:8003/health && echo "Service Emprunts OK"     || echo "Service Emprunts KO"
                    curl -f http://localhost:80          && echo "Frontend OK"             || echo "Frontend KO"
                '''
            }
        }
    }

    post {

        success {
            echo 'DEPLOIEMENT REUSSI - Application accessible sur http://localhost'
        }

        failure {
            echo 'ECHEC DU PIPELINE - Verifier les logs ci-dessus'
            sh 'docker compose -f ${DOCKER_COMPOSE_FILE} down || true'
        }

        always {
            echo 'Pipeline termine - consulter les logs pour les details'
        }
    }
}
