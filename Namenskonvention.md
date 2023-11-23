1. Versionierung
API-Versionierung ist entscheidend, um Kompatibilität sicherzustellen.
Verwenden Sie im Endpunkt-Pfad oder in den Headern klare Versionierungsinformationen.
Beispiel: /api/v1/resource oder Accept: application/vnd.company.v1+json
Quellen:

Richardson, L., & Amundsen, M. (2013). RESTful Web APIs. O'Reilly Media.
SemVer

2. Namenskonventionen
Nutzen Sie aussagekräftige, konsistente Ressourcennamen.
Verwenden Sie Singular oder Plural konsequent (aber nicht gemischt).
Vermeiden Sie zu lange oder abgekürzte Namen.
Beispiel: /users statt /userlist oder /getUsers
Quellen:

Fielding, R. T. (2000). Architectural Styles and the Design of Network-based Software Architectures.
Microsoft REST API Guidelines

3. Korrekter Einsatz der HTTP-Methoden
Verwenden Sie HTTP-Methoden gemäß ihrer semantischen Bedeutung.
GET für das Abrufen von Daten.
POST zum Erstellen von Ressourcen.
PUT oder PATCH zum Aktualisieren von Ressourcen.
DELETE zum Löschen von Ressourcen.
Quellen:

RFC 7231 - Hypertext Transfer Protocol (HTTP/1.1): Semantics and Content
RESTful API Design: Best Practices in a Nutshell