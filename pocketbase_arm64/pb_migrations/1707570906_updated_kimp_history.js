/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("j23l704r2fn2hbi")

  collection.name = "history"

  return dao.saveCollection(collection)
}, (db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("j23l704r2fn2hbi")

  collection.name = "kimp_history"

  return dao.saveCollection(collection)
})
