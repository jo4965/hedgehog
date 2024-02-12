/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("deeimxbh1lbz3gg")

  // add
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "klzqrjzj",
    "name": "KRW_price",
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

  // add
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "cto0mtal",
    "name": "USD_price",
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
  collection.schema.removeField("klzqrjzj")

  // remove
  collection.schema.removeField("cto0mtal")

  return dao.saveCollection(collection)
})
