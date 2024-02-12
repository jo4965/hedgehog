/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("2jyut262u9nev34")

  // remove
  collection.schema.removeField("gvapl6ep")

  return dao.saveCollection(collection)
}, (db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("2jyut262u9nev34")

  // add
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "gvapl6ep",
    "name": "KRW_amount_to_buy",
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
