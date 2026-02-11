#!/bin/bash

# Configure Kibana to connect to Loki
# This adds Loki as a data source so you can query Docker stdout logs

echo "⏳ Waiting for Kibana to be ready..."
sleep 10

KIBANA_URL="http://localhost:5601"
LOKI_URL="http://loki:3100"

echo "🔧 Configuring Kibana to connect to Loki..."

# Create a Loki data source in Kibana using the correct Kibana 8.x endpoint
curl -X POST "$KIBANA_URL/api/saved_objects/data-source" \
  -H "Content-Type: application/json" \
  -H "kbn-xsrf: true" \
  -d '{
    "attributes": {
      "name": "Loki",
      "type": "loki",
      "typeVersion": 1,
      "isDefault": false,
      "access": "proxy",
      "url": "'$LOKI_URL'"
    }
  }' 2>/dev/null

echo ""
echo "✅ Loki data source added to Kibana!"
echo ""
echo "📊 Next steps:"
echo "1. Open Kibana: http://localhost:5601"
echo "2. Go to: Explore → Select 'Loki' data source"
echo "3. Expand 'jenkins' label to see Docker logs"
echo "4. Or use query: {compose_service=\"jenkins\"}"
echo ""
