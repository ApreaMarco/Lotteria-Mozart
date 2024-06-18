from pyscript import document
class DOMDict:
    def __getitem__(self, key):
        # Accedi all'elemento DOM tramite l'ID quando viene utilizzata la sintassi delle parentesi quadre
        element = document.getElementById(key)
        # Restituisci un'istanza di DOMElementWrapper invece dell'elemento DOM diretto
        return element
