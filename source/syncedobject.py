from source.game import *

class SyncedObject:
    id_counter = 0
    objects = {}
    destroyed_ids = []

    def on_delete(self):
        print("Sending Synced Object Destroyed Message for " + str(self.id))
        SyncedObject.destroyed_ids.append(self.id)

    def __del__(self):
        print("Destroyed Synced Object " + str(self.id))
        try:
            del SyncedObject.objects[self.id]
        except KeyError as e:
            pass


    def __init__(self, id=None, **kwargs):
        if id is None:
            print("Assigned Synced Object ID...")
            if Game().Client:
                print("ERROR: SyncedObject has no ID on client")
            self.id = SyncedObject.id_counter + 1
            SyncedObject.id_counter += 1
        else:
            self.id = id

        print("Created Synced Object " + str(self.id) + " - " + str(self))
        SyncedObject.objects[self.id] = self

        if Game().Server:
            self._dirty_creation = True

    def update_connected(self, client):
        pass

    def update_sync(self, client):
        pass

    def update_network(self, client):
        if self._dirty_creation:
            self.update_connected(client)
        else:
            self.update_sync(client)

