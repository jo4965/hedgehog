/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("deeimxbh1lbz3gg")

  // add
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "5o9xu1ie",
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
  const collection = dao.findCollectionByNameOrId("deeimxbh1lbz3gg")

  // remove
  collection.schema.removeField("5o9xu1ie")

  return dao.saveCollection(collection)
})
