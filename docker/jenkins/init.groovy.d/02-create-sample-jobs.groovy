#!groovy

import jenkins.model.*
import hudson.model.*
import hudson.tasks.*

def instance = Jenkins.getInstance()

println "--> Creating sample jobs"

// Create a simple freestyle job
def jobName1 = "sample-build-job"
def job1 = instance.getItem(jobName1)
if (job1 == null) {
    def project1 = instance.createProject(FreeStyleProject, jobName1)
    project1.setDescription("Sample build job for testing")
    
    // Add a simple shell build step
    def shellStep1 = new Shell("""
echo "Building project..."
sleep 2
echo "Build completed successfully"
    """)
    project1.getBuildersList().add(shellStep1)
    project1.save()
    
    println "--> Created job: $jobName1"
}

// Create another freestyle job
def jobName2 = "test-job"
def job2 = instance.getItem(jobName2)
if (job2 == null) {
    def project2 = instance.createProject(FreeStyleProject, jobName2)
    project2.setDescription("Test job for CI/CD pipeline")
    
    def shellStep2 = new Shell("""
echo "Running tests..."
sleep 3
echo "All tests passed"
    """)
    project2.getBuildersList().add(shellStep2)
    project2.save()
    
    println "--> Created job: $jobName2"
}

// Create a deployment job
def jobName3 = "deploy-to-production"
def job3 = instance.getItem(jobName3)
if (job3 == null) {
    def project3 = instance.createProject(FreeStyleProject, jobName3)
    project3.setDescription("Production deployment job")
    
    def shellStep3 = new Shell("""
echo "Deploying to production..."
sleep 5
echo "Deployment completed"
    """)
    project3.getBuildersList().add(shellStep3)
    project3.save()
    
    println "--> Created job: $jobName3"
}

instance.save()

println "--> Sample jobs creation completed"
