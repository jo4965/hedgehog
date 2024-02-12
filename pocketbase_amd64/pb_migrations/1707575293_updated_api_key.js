/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("2jyut262u9nev34")

  // remove
  collection.schema.removeField("opdjasna")

  // add
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "zjre87qi",
    "name": "binance_leverage",
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
}, (db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("2jyut262u9nev34")

  // add
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "opdjasna",
    "name": "KRW_amount_to_buy",
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

  // remove
  collection.schema.removeField("zjre87qi")

  // remove
  collection.schema.removeField("gvapl6ep")

  return dao.saveCollection(collection)
})
