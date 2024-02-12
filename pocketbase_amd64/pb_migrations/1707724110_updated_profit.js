/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("9ecrdo31p2rir9t")

  // add
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "5nnlsm3f",
    "name": "user_name",
    "type": "text",
    "required": false,
    "presentable": false,
    "unique": false,
    "options": {
      "min": null,
      "max": null,
      "pattern": ""
    }
  }))

  return dao.saveCollection(collection)
}, (db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("9ecrdo31p2rir9t")

  // remove
  collection.schema.removeField("5nnlsm3f")

  return dao.saveCollection(collection)
})
