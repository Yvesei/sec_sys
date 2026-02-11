import java.util.logging.Level
import java.util.logging.Logger

def root = Logger.getLogger("")
root.setLevel(Level.FINEST)

def setLevel = { name ->
    try {
        Logger.getLogger(name).setLevel(Level.FINEST)
    } catch (Exception e) {
        println "Could not set logging level for ${name}: ${e}"
    }
}

setLevel('hudson')
setLevel('org.jenkinsci')
setLevel('jenkins')
setLevel('org.eclipse.jetty')

println "99-debug-logging.groovy: set Jenkins log levels to FINEST"
