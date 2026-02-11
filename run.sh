#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project directories
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCKER_DIR="$PROJECT_DIR/docker"
SCRIPTS_DIR="$PROJECT_DIR/scripts"

# Service URLs
JENKINS_URL="http://localhost:8080"
KIBANA_URL="http://localhost:5601"
ELASTICSEARCH_URL="http://localhost:9200"

# Function to print colored messages
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to check if a service is ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=60
    local attempt=0

    print_message "$YELLOW" "⏳ Waiting for $service_name to be ready..."
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            print_message "$GREEN" "✅ $service_name is ready!"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 5
    done
    
    print_message "$RED" "❌ $service_name failed to start within timeout"
    return 1
}

# Function to start all services
start_services() {
    print_message "$BLUE" "🚀 Starting all services..."
    
    cd "$DOCKER_DIR"
    docker-compose up -d
    
    if [ $? -eq 0 ]; then
        print_message "$GREEN" "✅ Services started successfully"
        
        # Wait for services to be ready
        wait_for_service "$ELASTICSEARCH_URL" "Elasticsearch"
        wait_for_service "$KIBANA_URL/api/status" "Kibana"
        wait_for_service "$JENKINS_URL" "Jenkins"
        
        print_message "$GREEN" "
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   🎉 All services are ready!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   Jenkins:        $JENKINS_URL
   Username:       admin
   Password:       admin123

   Kibana:         $KIBANA_URL
   Elasticsearch:  $ELASTICSEARCH_URL

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    else
        print_message "$RED" "❌ Failed to start services"
        return 1
    fi
}

# Function to setup Kibana
setup_kibana() {
    print_message "$BLUE" "🔧 Setting up Kibana..."
    
    if ! wait_for_service "$KIBANA_URL/api/status" "Kibana"; then
        print_message "$RED" "❌ Kibana is not available"
        return 1
    fi
    
    cd "$PROJECT_DIR"
    python3 "$SCRIPTS_DIR/setup_kibana.py"
    
    if [ $? -eq 0 ]; then
        print_message "$GREEN" "✅ Kibana setup completed"
    else
        print_message "$RED" "❌ Kibana setup failed"
        return 1
    fi
}

# Function to run normal scenarios
run_normal_scenarios() {
    print_message "$BLUE" "👤 Running normal usage scenarios..."
    
    if ! wait_for_service "$JENKINS_URL" "Jenkins"; then
        print_message "$RED" "❌ Jenkins is not available"
        return 1
    fi
    
    cd "$PROJECT_DIR"
    python3 "$SCRIPTS_DIR/normal_scenarios.py"
    
    if [ $? -eq 0 ]; then
        print_message "$GREEN" "✅ Normal scenarios completed"
    else
        print_message "$RED" "❌ Normal scenarios failed"
        return 1
    fi
}

# Function to run attack scenarios
run_attack_scenarios() {
    print_message "$BLUE" "🔴 Running attack scenarios..."
    
    if ! wait_for_service "$JENKINS_URL" "Jenkins"; then
        print_message "$RED" "❌ Jenkins is not available"
        return 1
    fi
    
    cd "$PROJECT_DIR"
    python3 "$SCRIPTS_DIR/attack_scenarios.py"
    
    if [ $? -eq 0 ]; then
        print_message "$GREEN" "✅ Attack scenarios completed"
    else
        print_message "$RED" "❌ Attack scenarios failed"
        return 1
    fi
}

# Function to run full demo
run_full_demo() {
    print_message "$BLUE" "🎬 Running full demonstration..."
    
    start_services || return 1
    sleep 10
    setup_kibana || return 1
    sleep 5
    run_normal_scenarios || return 1
    sleep 5
    run_attack_scenarios || return 1
    
    print_message "$GREEN" "
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ✅ Full demonstration completed!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   You can now access:
   - Kibana: $KIBANA_URL
   - Jenkins: $JENKINS_URL

   To view logs in Kibana:
   1. Go to Discover
   2. Select 'jenkins-logs-*' index pattern
   3. Filter for attacks or normal traffic

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Function to show service logs
show_logs() {
    print_message "$BLUE" "📋 Showing service logs..."
    
    echo "Which service logs do you want to see?"
    echo "1) Jenkins"
    echo "2) Elasticsearch"
    echo "3) Logstash"
    echo "4) Filebeat"
    echo "5) Kibana"
    echo "6) All services"
    read -p "Enter choice [1-6]: " choice
    
    cd "$DOCKER_DIR"
    case $choice in
        1) docker-compose logs -f jenkins ;;
        2) docker-compose logs -f elasticsearch ;;
        3) docker-compose logs -f logstash ;;
        4) docker-compose logs -f filebeat ;;
        5) docker-compose logs -f kibana ;;
        6) docker-compose logs -f ;;
        *) print_message "$RED" "Invalid choice" ;;
    esac
}

# Function to stop all services
stop_services() {
    print_message "$BLUE" "🛑 Stopping all services..."
    
    cd "$DOCKER_DIR"
    docker-compose down
    
    if [ $? -eq 0 ]; then
        print_message "$GREEN" "✅ Services stopped successfully"
    else
        print_message "$RED" "❌ Failed to stop services"
        return 1
    fi
}

# Function to cleanup all data
cleanup() {
    print_message "$YELLOW" "⚠️  This will remove all data and volumes. Are you sure? (y/N)"
    read -r response
    
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_message "$BLUE" "🧹 Cleaning up all data..."
        
        cd "$DOCKER_DIR"
        docker-compose down -v
        
        if [ $? -eq 0 ]; then
            print_message "$GREEN" "✅ Cleanup completed"
        else
            print_message "$RED" "❌ Cleanup failed"
            return 1
        fi
    else
        print_message "$YELLOW" "Cleanup cancelled"
    fi
}

# Function to check prerequisites
check_prerequisites() {
    print_message "$BLUE" "🔍 Checking prerequisites..."
    
    local all_ok=true
    
    # Check Docker
    if command -v docker &> /dev/null; then
        print_message "$GREEN" "✅ Docker is installed"
    else
        print_message "$RED" "❌ Docker is not installed"
        all_ok=false
    fi
    
    # Check Docker Compose
    if command -v docker-compose &> /dev/null; then
        print_message "$GREEN" "✅ Docker Compose is installed"
    else
        print_message "$RED" "❌ Docker Compose is not installed"
        all_ok=false
    fi
    
    # Check Python 3
    if command -v python3 &> /dev/null; then
        print_message "$GREEN" "✅ Python 3 is installed"
    else
        print_message "$RED" "❌ Python 3 is not installed"
        all_ok=false
    fi
    
    if [ "$all_ok" = false ]; then
        print_message "$RED" "
Please install missing prerequisites:
- Docker: https://docs.docker.com/get-docker/
- Docker Compose: https://docs.docker.com/compose/install/
- Python 3: https://www.python.org/downloads/"
        return 1
    fi
    
    print_message "$GREEN" "✅ All prerequisites are met"
}

# Main menu
show_menu() {
    echo ""
    print_message "$BLUE" "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    print_message "$BLUE" "   Jenkins Security Log Analysis Project"
    print_message "$BLUE" "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "1) Start all services              - Start Jenkins + ELK Stack"
    echo "2) Setup Kibana                    - Configure Kibana dashboards"
    echo "3) Run normal usage scenarios      - Generate legitimate traffic"
    echo "4) Run attack scenarios            - Generate malicious traffic"
    echo "5) Run full demo                   - Complete demonstration"
    echo "6) Show service logs               - View Docker container logs"
    echo "7) Stop all services               - Stop all Docker containers"
    echo "8) Cleanup                         - Remove all data and volumes"
    echo "9) Check prerequisites             - Verify system requirements"
    echo "10) Exit                           - Exit the script"
    echo ""
}

# Main loop
main() {
    while true; do
        show_menu
        read -p "Enter your choice [1-10]: " choice
        
        case $choice in
            1) start_services ;;
            2) setup_kibana ;;
            3) run_normal_scenarios ;;
            4) run_attack_scenarios ;;
            5) run_full_demo ;;
            6) show_logs ;;
            7) stop_services ;;
            8) cleanup ;;
            9) check_prerequisites ;;
            10)
                print_message "$GREEN" "👋 Goodbye!"
                exit 0
                ;;
            *)
                print_message "$RED" "❌ Invalid choice. Please try again."
                ;;
        esac
        
        echo ""
        read -p "Press Enter to continue..."
    done
}

# Run main function
main
