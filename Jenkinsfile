#!/usr/bin/env groovy

pipeline {
  agent { label 'executor-v2' }

  options {
    timestamps()
    buildDiscarder(logRotator(numToKeepStr: '30'))
  }

  parameters {
    booleanParam(name: 'PUBLISH_TO_PYPI', defaultValue: false, description: 'Boolean condition for whether we need to publish the package to PyPi')
  }

  triggers {
    cron(getDailyCronString())
  }

   stages {
    stage('Linting') {
      parallel {
        stage('Code') {
          steps { sh './bin/test_linting' }
        }

        stage('Changelog') {
          steps { sh './bin/test_changelog' }
        }
      }
    }

    stage('Unit tests') {
      steps {
        sh './bin/test_unit'
      }
      post {
        always {
          junit 'output/**/*.xml'
          cobertura autoUpdateHealth: false, autoUpdateStability: false, coberturaReportFile: 'coverage.xml', conditionalCoverageTargets: '50, 0, 50', failUnhealthy: true, failUnstable: false, lineCoverageTargets: '50, 0, 50', maxNumberOfBuilds: 0, methodCoverageTargets: '50, 0, 50', onlyStable: false, sourceEncoding: 'ASCII', zoomCoverageChart: false
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

    stage('RHEL8 Integration tests') {
      steps {
        sh 'summon -e common ./bin/test_integration_rhel8'
      }

      post {
        always {
          junit 'output/**/*.xml'
        }
      }
    }

    stage('Scan Docker image') {
      parallel {
        stage('Scan Docker image for fixable vulns') {
          steps {
            scanAndReport("conjur-python-cli:latest", "HIGH", false)
          }
        }

        stage('Scan Docker image for total vulns') {
          steps {
            scanAndReport("conjur-python-cli:latest", "NONE", true)
          }
        }
      }

      when {
        branch "main"
      }
    }

    stage('Publish') {
      parallel {
        // Only publish if the HEAD is tagged with the same version as in __version__.py
        stage('Publish to PyPI') {
          steps {
            sh 'summon -e production ./bin/publish_package'
          }
          when {
            expression { params.PUBLISH_TO_PYPI == true }
          }
        }

        stage('Publish containers') {
          steps {
            sh './bin/publish_container'
          }
          when {
            branch "main"
          }
        }
      }
    }
  }

  post {
    always {
      cleanupAndNotify(currentBuild.currentResult)
    }
    unsuccessful {
      script {
        if (env.BRANCH_NAME == 'main') {
          cleanupAndNotify(currentBuild.currentResult, "#development", "@PalmTree")
        } else {
          cleanupAndNotify(currentBuild.currentResult, "#development")
        }
      }
    }
  }
}
