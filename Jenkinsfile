// Pipeline CI/CD - Bibliotheque Numerique DIT
// Groupe 2 - Master 1 IA - Dakar Institute of Technology

pipeline {

    agent any

    environment {
        PROJECT_NAME       = "bibliotheque-dit"
        COMPOSE_FILE       = "docker-compose.yml"
        FRONTEND_PORT      = "80"
        LIVRES_PORT        = "8001"
        UTILISATEURS_PORT  = "8002"
        EMPRUNTS_PORT      = "8003"
    }

    options {
        timeout(time: 15, unit: 'MINUTES')
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '5'))
    }

    stages {

        stage('Recuperation du code') {
            steps {
                echo '====== ETAPE 1 : Recuperation du code source ======'
                checkout scm
                echo 'Code recupere avec succes'
            }
        }

        stage('Verification de la structure') {
            steps {
                echo '====== ETAPE 2 : Verification de la structure du projet ======'
                script {
                    def fichiers = [
                        'docker-compose.yml',
                        'frontend/Dockerfile',
                        'frontend/index.html',
                        'service-livres/Dockerfile',
                        'service-livres/main.py',
                        'service-livres/requirements.txt',
                        'service-utilisateurs/Dockerfile',
                        'service-utilisateurs/main.py',
                        'service-utilisateurs/requirements.txt',
                        'service-emprunts/Dockerfile',
                        'service-emprunts/main.py',
                        'service-emprunts/requirements.txt'
                    ]
                    for (f in fichiers) {
                        if (!fileExists(f)) {
                            error "Fichier manquant : ${f}"
                        }
                        echo "  OK : ${f}"
                    }
                }
                echo 'Structure du projet validee'
            }
        }

        stage('Build des images Docker') {
            steps {
                echo '====== ETAPE 3 : Construction des images Docker ======'
                sh 'docker compose -f ${COMPOSE_FILE} build --no-cache'
                echo 'Images construites avec succes'
            }
        }

        stage('Arret de l ancienne version') {
            steps {
                echo '====== ETAPE 4 : Arret des anciens conteneurs ======'
                sh 'docker compose -f ${COMPOSE_FILE} down --remove-orphans || true'
                echo 'Environnement nettoye'
            }
        }

        stage('Deploiement') {
            steps {
                echo '====== ETAPE 5 : Deploiement des conteneurs ======'
                sh 'docker compose -f ${COMPOSE_FILE} up -d'
                echo 'Conteneurs demarres'
            }
        }

        stage('Verification sante des services') {
            steps {
                echo '====== ETAPE 6 : Verification de sante ======'
                sh '''
                    echo "Attente du demarrage des services (20s)..."
                    sleep 20

                    echo ""
                    echo "--- Verification du service Livres (port ${LIVRES_PORT}) ---"
                    curl -sf http://localhost:${LIVRES_PORT}/health && echo " => Service Livres OK" || echo " => Service Livres KO"

                    echo ""
                    echo "--- Verification du service Utilisateurs (port ${UTILISATEURS_PORT}) ---"
                    curl -sf http://localhost:${UTILISATEURS_PORT}/health && echo " => Service Utilisateurs OK" || echo " => Service Utilisateurs KO"

                    echo ""
                    echo "--- Verification du service Emprunts (port ${EMPRUNTS_PORT}) ---"
                    curl -sf http://localhost:${EMPRUNTS_PORT}/health && echo " => Service Emprunts OK" || echo " => Service Emprunts KO"

                    echo ""
                    echo "--- Verification du Frontend (port ${FRONTEND_PORT}) ---"
                    curl -sf http://localhost:${FRONTEND_PORT} > /dev/null && echo " => Frontend OK" || echo " => Frontend KO"
                '''
            }
        }

        stage('Tests fonctionnels') {
            steps {
                echo '====== ETAPE 7 : Tests fonctionnels de base ======'
                sh '''
                    echo "--- Test POST /livres ---"
                    RESULT=$(curl -sf -X POST http://localhost:${LIVRES_PORT}/livres \
                        -H "Content-Type: application/json" \
                        -d '{"titre":"Livre Test CI","auteur":"Jenkins","isbn":"999-CI-TEST","annee":2025,"genre":"Test"}' \
                        -w "%{http_code}" -o /dev/null) || true
                    echo "Code HTTP : $RESULT"

                    echo ""
                    echo "--- Test GET /livres ---"
                    curl -sf http://localhost:${LIVRES_PORT}/livres | head -c 200
                    echo ""

                    echo ""
                    echo "--- Test GET /utilisateurs ---"
                    curl -sf http://localhost:${UTILISATEURS_PORT}/utilisateurs | head -c 200
                    echo ""

                    echo ""
                    echo "Tests fonctionnels termines"
                '''
            }
        }
    }

    post {

        success {
            echo '''
============================================================
  DEPLOIEMENT REUSSI
  Application accessible sur http://localhost
  -  Frontend Vue.js    : http://localhost:80
  -  Service Livres     : http://localhost:8001/docs
  -  Service Utilisateurs : http://localhost:8002/docs
  -  Service Emprunts   : http://localhost:8003/docs
============================================================
            '''
        }

        failure {
            echo 'ECHEC DU PIPELINE - Nettoyage en cours...'
            sh 'docker compose -f ${COMPOSE_FILE} logs --tail=30 || true'
            sh 'docker compose -f ${COMPOSE_FILE} down || true'
        }

        always {
            echo 'Pipeline termine - Groupe 2 DIT M1 IA'
        }
    }
}
