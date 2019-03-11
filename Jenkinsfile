#!/usr/bin/env groovy

pipeline {
  agent { label 'executor-v2' }

  options {
    timestamps()
    buildDiscarder(logRotator(numToKeepStr: '30'))
  }

  stages {
    stage('Linting') {
      steps {
        sh 'true'
      }
    }

    stage('Unit tests') {
      steps {
        sh './bin/test'
      }

      post {
        always {
          junit 'output/**/*.xml'
        }
      }
    }

    stage('Integration tests') {
      steps {
        // sh './bin/test_integration'
        sh 'true'
      }

      post {
        always {
          junit 'output/**/*.xml'
        }
      }
    }
  }

  post {
    always {
      cleanupAndNotify(currentBuild.currentResult)
    }
  }
}
