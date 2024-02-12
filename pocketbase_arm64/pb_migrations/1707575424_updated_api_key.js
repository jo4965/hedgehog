/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("2jyut262u9nev34")

  // add
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "5rxqbi4w",
    "name": "hedge_alert_password",
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
  const collection = dao.findCollectionByNameOrId("2jyut262u9nev34")

  // remove
  collection.schema.removeField("5rxqbi4w")

  return dao.saveCollection(collection)
})
