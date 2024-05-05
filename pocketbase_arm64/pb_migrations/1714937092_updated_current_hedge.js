/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("deeimxbh1lbz3gg")

  // add
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "rs0ykxwz",
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
  const collection = dao.findCollectionByNameOrId("deeimxbh1lbz3gg")

  // remove
  collection.schema.removeField("rs0ykxwz")

  return dao.saveCollection(collection)
})
