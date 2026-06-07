// Script pour migrer les utilisateurs du localStorage vers le backend
const migrateUsersToBackend = async () => {
  // Récupérer les utilisateurs du localStorage
  const storedUsers = localStorage.getItem('techsearch_users')
  if (!storedUsers) {
    console.log('Aucun utilisateur à migrer')
    return
  }
  
  const users = JSON.parse(storedUsers)
  console.log(`Migration de ${users.length} utilisateur(s)...`)
  
  // Pour chaque utilisateur, envoyer une requête au backend
  for (const user of users) {
    try {
      const response = await fetch('http://localhost:8000/api/auth/migrate-user', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Migration-Key': 'your-migration-secret-key'
        },
        body: JSON.stringify({
          id: user.id,
          email: user.email,
          name: user.name,
          role: user.role,
          isActive: user.isActive,
          createdAt: user.createdAt,
          lastLogin: user.lastLogin
        })
      })
      
      if (response.ok) {
        console.log(`✓ Utilisateur ${user.email} migré`)
      } else {
        console.error(`✗ Erreur pour ${user.email}:`, await response.text())
      }
    } catch (error) {
      console.error(`✗ Erreur réseau pour ${user.email}:`, error.message)
    }
  }
  
  console.log('Migration terminée')
}

// Exécuter la migration
migrateUsersToBackend()