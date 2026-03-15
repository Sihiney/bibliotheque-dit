// ══════════════════════════════════════════════════════════
//  BIBLIOTHÈQUE NUMÉRIQUE DIT — Pipeline Jenkins CI/CD
//  Ce fichier décrit les étapes automatiques à chaque push
// ══════════════════════════════════════════════════════════

pipeline {

    // Exécuter sur n'importe quel agent disponible
    agent any

    // ── VARIABLES GLOBALES ──────────────────────────────
    environment {
        PROJECT_NAME = "bibliotheque-dit"
        DOCKER_COMPOSE_FILE = "docker-compose.yml"
    }

    // ── ÉTAPES DU PIPELINE ──────────────────────────────
    stages {

        // ÉTAPE 1 : Récupérer le code depuis GitHub
        stage('Récupération du code') {
            steps {
                echo '📥 Récupération du code depuis GitHub...'
                checkout scm   // Prend le code du dépôt GitHub configuré dans Jenkins
                echo '✅ Code récupéré avec succès'
            }
        }

        // ÉTAPE 2 : Vérifier que les fichiers essentiels sont présents
        stage('Vérification du projet') {
            steps {
                echo '🔍 Vérification de la structure du projet...'
                sh '''
                    echo "Structure du projet :"
                    ls -la

                    echo "Vérification des Dockerfiles..."
                    test -f service-livres/Dockerfile       && echo "✅ Dockerfile livres OK"
                    test -f service-utilisateurs/Dockerfile && echo "✅ Dockerfile utilisateurs OK"
                    test -f service-emprunts/Dockerfile     && echo "✅ Dockerfile emprunts OK"
                    test -f frontend/Dockerfile             && echo "✅ Dockerfile frontend OK"
                    test -f docker-compose.yml              && echo "✅ docker-compose.yml OK"
                '''
            }
        }

        // ÉTAPE 3 : Construire les images Docker
        stage('Build des images Docker') {
            steps {
                echo '🐳 Construction des images Docker...'
                sh 'docker compose -f ${DOCKER_COMPOSE_FILE} build --no-cache'
                echo '✅ Images construites avec succès'
            }
        }

        // ÉTAPE 4 : Arrêter l'ancienne version si elle tourne
        stage('Arrêt de l\'ancienne version') {
            steps {
                echo '🛑 Arrêt des anciens conteneurs...'
                sh 'docker compose -f ${DOCKER_COMPOSE_FILE} down --remove-orphans || true'
                // Le "|| true" évite que l'étape échoue si rien ne tourne
                echo '✅ Anciens conteneurs arrêtés'
            }
        }

        // ÉTAPE 5 : Déployer la nouvelle version
        stage('Déploiement') {
            steps {
                echo '🚀 Démarrage des nouveaux conteneurs...'
                sh 'docker compose -f ${DOCKER_COMPOSE_FILE} up -d'
                // -d = détaché (tourne en arrière-plan)
                echo '✅ Application déployée'
            }
        }

        // ÉTAPE 6 : Vérifier que tout tourne bien
        stage('Vérification santé des services') {
            steps {
                echo '🩺 Vérification des services...'
                sh '''
                    # Attendre 15 secondes que les services démarrent
                    sleep 15

                    # Tester chaque service
                    curl -f http://localhost:8001/health && echo "✅ Service Livres OK"       || echo "❌ Service Livres KO"
                    curl -f http://localhost:8002/health && echo "✅ Service Utilisateurs OK" || echo "❌ Service Utilisateurs KO"
                    curl -f http://localhost:8003/health && echo "✅ Service Emprunts OK"     || echo "❌ Service Emprunts KO"
                    curl -f http://localhost:80          && echo "✅ Frontend OK"             || echo "❌ Frontend KO"
                '''
            }
        }
    }

    // ── ACTIONS APRÈS LE PIPELINE ───────────────────────
    post {

        success {
            echo '''
            ╔══════════════════════════════════════╗
            ║  ✅  DÉPLOIEMENT RÉUSSI               ║
            ║  L application est accessible sur :  ║
            ║  http://localhost                    ║
            ╚══════════════════════════════════════╝
            '''
        }

        failure {
            echo '''
            ╔══════════════════════════════════════╗
            ║  ❌  ÉCHEC DU PIPELINE                ║
            ║  Vérifier les logs ci-dessus         ║
            ╚══════════════════════════════════════╝
            '''
            // Arrêter les conteneurs en cas d'échec
            sh 'docker compose -f ${DOCKER_COMPOSE_FILE} down || true'
        }

        always {
            echo '📋 Pipeline terminé — consulter les logs pour les détails'
        }
    }
}
