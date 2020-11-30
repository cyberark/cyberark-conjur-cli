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
    // Pack into executable
    stage('Pack into executable') {
      steps {
        script {
          // Node is used to pack the CLI into a window's executable
          node('executor-windows-2016-containers'){
            powershell """
            ./bin/pack_executable_windows
            """
          }
        }
      }
    }
  }
}
