/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("9ecrdo31p2rir9t")

  // update
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "j76y2ars",
    "name": "split_level",
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
  const collection = dao.findCollectionByNameOrId("9ecrdo31p2rir9t")

  // update
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "j76y2ars",
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
})
