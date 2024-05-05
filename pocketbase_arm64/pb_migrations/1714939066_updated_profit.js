/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("9ecrdo31p2rir9t")

  // add
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "xjvj50yt",
    "name": "split_value",
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

  // remove
  collection.schema.removeField("xjvj50yt")

  return dao.saveCollection(collection)
})
