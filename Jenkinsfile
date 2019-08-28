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
        sh './bin/test_linting'
      }
    }

    stage('Unit tests') {
      steps {
        sh './bin/test_unit'
      }

      post {
        always {
          junit 'output/**/*.xml'
          cobertura autoUpdateHealth: true, autoUpdateStability: true, coberturaReportFile: 'coverage.xml', conditionalCoverageTargets: '100, 0, 0', failUnhealthy: true, failUnstable: false, lineCoverageTargets: '100, 0, 0', maxNumberOfBuilds: 0, methodCoverageTargets: '100, 0, 0', onlyStable: false, sourceEncoding: 'ASCII', zoomCoverageChart: false
          ccCoverage("coverage.py")
        }
      }
    }

    stage('Integration tests') {
      steps {
        sh './bin/test_integration'
      }

      post {
        always {
          junit 'output/**/*.xml'
        }
      }
    }

    // Only publish to PyPI if the HEAD is
    // tagged with the same version as in __version__.py
    stage('Publish to PyPI') {
      steps {
        sh 'summon -e production ./bin/publish'
      }

      when {
        branch "master"
      }
    }
  }

  post {
    always {
      cleanupAndNotify(currentBuild.currentResult)
    }
  }
}
