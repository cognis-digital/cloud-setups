param location string = resourceGroup().location
resource env 'Microsoft.App/managedEnvironments@2023-05-01' = { name: 'cognis-env', location: location, properties: {} }
resource app 'Microsoft.App/containerApps@2023-05-01' = {
  name: 'cognis-app', location: location
  properties: {
    managedEnvironmentId: env.id
    configuration: { ingress: { external: true, targetPort: 8000 } }
    template: { containers: [ { name: 'app', image: 'ghcr.io/cognis-digital/app:latest' } ] }
  }
}
