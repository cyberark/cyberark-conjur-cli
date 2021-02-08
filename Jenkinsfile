#!/usr/bin/env groovy

pipeline {
  agent { label 'executor-v2' }

  options {
    timestamps()
    buildDiscarder(logRotator(numToKeepStr: '30'))
  }

  triggers {
    cron(getDailyCronString())
  }

  stages {
    stage('RHEL 8 Node') {
      // Node used to deploy RHEL 8 machines and pack the CLI executable
      agent { label 'executor-v2-rhel-ee' }

      steps {
        sh '''
        sudo yum install python38 -y && \
          sudo yum install binutils -y && \
          sudo pip3 install pyinstaller
        python3 -m venv venv
        source venv/bin/activate
        pip3 install -r requirements.txt
        pyinstaller -F ./pkg_bin/conjur
        '''
        archiveArtifacts artifacts: 'dist/', fingerprint: true
      }
    }

//    stage('Linting') {
//      parallel {
//        stage('Code') {
//          steps { sh './bin/test_linting' }
//        }

//        stage('Changelog') {
//          steps { sh './bin/test_changelog' }
//        }
//      }
//    }

//    stage('Unit tests') {
//      steps {
//        sh './bin/test_unit'
//      }
//      post {
//        always {
//          junit 'output/**/*.xml'
//          cobertura autoUpdateHealth: false, autoUpdateStability: false, coberturaReportFile: 'coverage.xml', conditionalCoverageTargets: '50, 0, 50', failUnhealthy: true, failUnstable: false, lineCoverageTargets: '50, 0, 50', maxNumberOfBuilds: 0, methodCoverageTargets: '50, 0, 50', onlyStable: false, sourceEncoding: 'ASCII', zoomCoverageChart: false
//          ccCoverage("coverage.py")
//        }
//      }
//    }

//    stage('Integration tests') {
//      steps {
//        sh './bin/test_integration'
//      }

//      post {
//        always {
//          junit 'output/**/*.xml'
//        }
//      }
//    }

    // Only publish if the HEAD is tagged with the same version as in __version__.py
    stage('Publish') {
      parallel {
        stage('Publish to PyPI') {
          steps {
            sh 'summon -e production ./bin/publish_package'
          }

          when {
            branch "master"
          }
        }

        stage('Publish containers') {
          steps {
            sh './bin/publish_container'
          }

          when {
            branch "master"
          }
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
