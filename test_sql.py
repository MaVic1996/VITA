from vita.memory.sqlite import SQLitePreferencesRepository
from vita.memory.models import UserPreferences

repository = SQLitePreferencesRepository()
repository.save(UserPreferences(name="Víctor"))
print(repository.load())


