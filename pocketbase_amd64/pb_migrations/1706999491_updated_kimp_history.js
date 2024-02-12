/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("j23l704r2fn2hbi")

  // add
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "p99bf13x",
    "name": "leverage",
    "type": "number",
    "required": false,
    "presentable": false,
    "unique": false,
    "options": {
      "min": null,
      "max": null,
      "noDecimal": false
    }
  }))

  return dao.saveCollection(collection)
}, (db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("j23l704r2fn2hbi")

  // remove
  collection.schema.removeField("p99bf13x")

  return dao.saveCollection(collection)
})
