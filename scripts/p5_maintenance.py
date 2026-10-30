"""Explicit local maintenance for AgentMesh SQLite runs."""
import argparse
from agentmesh.storage import RunStore

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--database",required=True)
    parser.add_argument("--backup")
    parser.add_argument("--keep",type=int)
    args=parser.parse_args()
    database=RunStore(args.database)
    if args.backup:
        print("Backup:",database.backup(args.backup))
    if args.keep is not None:
        if not args.backup:
            parser.error("--keep requires --backup first")
        print("Deleted old runs:",database.prune(args.keep))
    if not args.backup and args.keep is None:
        parser.error("supply --backup and optionally --keep")

if __name__=="__main__":main()
