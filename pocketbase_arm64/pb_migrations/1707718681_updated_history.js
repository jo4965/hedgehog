/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("j23l704r2fn2hbi")

  // add
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "avcvsumj",
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
  const collection = dao.findCollectionByNameOrId("j23l704r2fn2hbi")

  // remove
  collection.schema.removeField("avcvsumj")

  return dao.saveCollection(collection)
})
