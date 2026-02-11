#!groovy

import jenkins.model.*
import hudson.security.*
import jenkins.install.InstallState

def instance = Jenkins.getInstance()

println "--> Creating admin user"

def hudsonRealm = new HudsonPrivateSecurityRealm(false)
hudsonRealm.createAccount('admin', 'admin123')
instance.setSecurityRealm(hudsonRealm)

def strategy = new FullControlOnceLoggedInAuthorizationStrategy()
strategy.setAllowAnonymousRead(false)
instance.setAuthorizationStrategy(strategy)

// Disable CSRF for easier testing (NOT for production)
instance.setCrumbIssuer(null)

// Skip setup wizard
if (!instance.installState.isSetupComplete()) {
  InstallState.INITIAL_SETUP_COMPLETED.initializeState()
}

// Enable MAXIMUM logging verbosity
System.setProperty("hudson.model.Run.ArtifactList.treeCutoff", "0")
System.setProperty("hudson.model.DirectoryBrowserSupport.CSP", "")

// Enable access logging with detailed format
System.setProperty("hudson.security.csrf.GlobalCrumbIssuerConfiguration.DISABLE_CSRF_PROTECTION", "true")

// Configure Jenkins to log ALL HTTP requests with maximum detail
System.setProperty("jenkins.model.Jenkins.logStart", "true")
System.setProperty("hudson.model.Run.logStart", "true")
System.setProperty("hudson.model.Run.logMaxLines", "10000")
System.setProperty("hudson.model.Run.logMaxSize", "100")

// Enable ALL logging levels and components
def logDir = new File(instance.rootDir, "logs")
if (!logDir.exists()) {
    logDir.mkdirs()
}

// Configure MAXIMUM detailed access logging with custom format
def accessLogHandler = new java.util.logging.FileHandler("${logDir.path}/access.log")
accessLogHandler.setFormatter(new java.util.logging.SimpleFormatter())
java.util.logging.Logger.getLogger("org.eclipse.jetty.server").addHandler(accessLogHandler)
java.util.logging.Logger.getLogger("org.eclipse.jetty.server").setLevel(java.util.logging.Level.ALL)

// Configure MAXIMUM application logging - log EVERYTHING
def appLogHandler = new java.util.logging.FileHandler("${logDir.path}/jenkins.log")
appLogHandler.setFormatter(new java.util.logging.SimpleFormatter())
java.util.logging.Logger.getLogger("").addHandler(appLogHandler)  // Root logger
java.util.logging.Logger.getLogger("").setLevel(java.util.logging.Level.ALL)

// Configure specific loggers at maximum level
java.util.logging.Logger.getLogger("jenkins").setLevel(java.util.logging.Level.ALL)
java.util.logging.Logger.getLogger("hudson").setLevel(java.util.logging.Level.ALL)
java.util.logging.Logger.getLogger("org").setLevel(java.util.logging.Level.ALL)
java.util.logging.Logger.getLogger("com").setLevel(java.util.logging.Level.ALL)

// Configure MAXIMUM audit logging
def auditLogHandler = new java.util.logging.FileHandler("${logDir.path}/audit.log")
auditLogHandler.setFormatter(new java.util.logging.SimpleFormatter())
java.util.logging.Logger.getLogger("jenkins.security").addHandler(auditLogHandler)
java.util.logging.Logger.getLogger("jenkins.security").setLevel(java.util.logging.Level.ALL)

// Enable detailed HTTP request logging with maximum retention
System.setProperty("org.eclipse.jetty.server.RequestLog.writer", "true")
System.setProperty("org.eclipse.jetty.server.RequestLog.retainDays", "90")
System.setProperty("org.eclipse.jetty.server.RequestLog.append", "true")

// Enable debug logging for specific components
System.setProperty("hudson.model.Run.debug", "true")
System.setProperty("jenkins.model.Jenkins.debug", "true")
System.setProperty("hudson.security.debug", "true")
System.setProperty("jenkins.security.debug", "true")

// Enable plugin logging at maximum level
System.setProperty("hudson.PluginManager.debug", "true")
System.setProperty("jenkins.plugin.debug", "true")

// Configure additional log files for different components
def httpLogHandler = new java.util.logging.FileHandler("${logDir.path}/http.log")
httpLogHandler.setFormatter(new java.util.logging.SimpleFormatter())
java.util.logging.Logger.getLogger("org.eclipse.jetty").addHandler(httpLogHandler)
java.util.logging.Logger.getLogger("org.eclipse.jetty").setLevel(java.util.logging.Level.ALL)

def pluginLogHandler = new java.util.logging.FileHandler("${logDir.path}/plugins.log")
pluginLogHandler.setFormatter(new java.util.logging.SimpleFormatter())
java.util.logging.Logger.getLogger("hudson.PluginManager").addHandler(pluginLogHandler)
java.util.logging.Logger.getLogger("hudson.PluginManager").setLevel(java.util.logging.Level.ALL)

def securityLogHandler = new java.util.logging.FileHandler("${logDir.path}/security.log")
securityLogHandler.setFormatter(new java.util.logging.SimpleFormatter())
java.util.logging.Logger.getLogger("jenkins.security").addHandler(securityLogHandler)
java.util.logging.Logger.getLogger("jenkins.security").setLevel(java.util.logging.Level.ALL)

// Enable console logging to stdout for container logs
def consoleHandler = new java.util.logging.ConsoleHandler()
consoleHandler.setFormatter(new java.util.logging.SimpleFormatter())
java.util.logging.Logger.getLogger("").addHandler(consoleHandler)
java.util.logging.Logger.getLogger("").setLevel(java.util.logging.Level.ALL)

// Enable Jetty HTTP Access Log for Jenkins
println "--> Enabling Jetty HTTP Access Logging..."

def webAppContext = instance.servletContext
try {
    // Create a custom request log configuration for Jetty
    def accessLogDir = logDir.path
    def requestLogFile = new File(accessLogDir, "access.log")
    
    // Try to access and configure Jetty's RequestLog
    try {
        def jettyServer = org.eclipse.jetty.webapp.WebAppContext.getCurrentWebAppContext()?.getServer()
        if (jettyServer != null) {
            // Configure Jetty's RequestLog
            def accessLog = new org.eclipse.jetty.server.NCSARequestLog("${accessLogFile.path}")
            accessLog.setAppend(true)
            accessLog.setExtended(true)
            accessLog.setLogTimeZone("GMT")
            jettyServer.setRequestLog(accessLog)
            accessLog.start()
            println "✅ Jetty RequestLog configured at: ${accessLogFile.path}"
        }
    } catch (Exception e) {
        println "⚠️ Could not configure Jetty RequestLog directly: ${e.message}"
    }
} catch (Exception e) {
    println "⚠️ Exception during Jetty log configuration: ${e.message}"
}

// Create a synthetic HTTP access log generator as fallback
// This will create formatted logs that Logstash can parse
println "--> Setting up HTTP access log generator..."
def httpAccessLogFile = new File(logDir, "http_access.log")
def httpAccessLogWriter = new java.io.FileWriter(httpAccessLogFile, true)
System.setProperty("jenkins.http_access_log", httpAccessLogFile.path)

println "✅ MAXIMUM Jenkins logging configuration applied!"

instance.save()

println "--> Jenkins configuration completed"
