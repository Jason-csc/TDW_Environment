from itertools import permutations
from random import shuffle, choice
import json

class Block:
    def __init__(self, id, bin):
        super(Block).__init__()
        assert((0 <= id) and (id < 27))
        self.id = id
        self.bin = bin
        
    def get_grounding(self):
        return f'==({self.id},@,{["A","B","C","D"][self.bin]})'
    
    def get_verbose_grounding(self):
        return ["inBin",self.id,["A","B","C","D"][self.bin]]
        
    def same_col(self, target):
        return self.bin%2 == target.bin%2 and not self.bin==target.bin
    
    def same_row(self, target):
        return self.bin//2 == target.bin//2 and not self.bin==target.bin
        
    def same_diag(self,target):
        return self.bin ^ target.bin == 3 and not self.bin==target.bin
    
    def same_bin(self,target):
        return self.bin==target.bin
        
    def get_relationships(self, target):
        retval = [
        f'{"==" if self.same_col(target) else "<>"}({self.id},|,{target.id})',
        f'{"==" if self.same_row(target) else "<>"}({self.id},-,{target.id})',
        f'{"==" if self.same_diag(target) else "<>"}({self.id},/,{target.id})',
        f'{"==" if self.same_bin(target) else "<>"}({self.id},U,{target.id})'
        ]
        return retval
        
    def get_verbose_relationships(self, target):
        retval = [
        ["same" if self.same_col(target) else "opposite",self.id,"column",target.id],
        ["same" if self.same_row(target) else "opposite",self.id,"row",target.id],
        ["same" if self.same_diag(target) else "opposite",self.id,"diagonal",target.id],
        ["same" if self.same_bin(target) else "other","bin",self.id,target.id]
        ]
        return retval
    
def game_maker(game, blocks):
    retval = []
    if blocks:
        if game:
            block = blocks[0]
            for node, _ in game:
                for rel in zip(node.get_relationships(block),node.get_verbose_relationships(block)):
                    if '==' in rel[0]:
                        retval += game_maker(game + [(block,rel[1])], blocks[1:])
        else:
            block = blocks[0]
            game.append((block,block.get_verbose_grounding()))
            retval += game_maker(game, blocks[1:])
    else:
        if game:
            retval += [[g[1] for g in game]]
    return retval
    
to_bits = lambda x: [x%2] if x < 2 else to_bits(x//2)+[x%2]
bit_count = lambda x: sum(to_bits(x))
        

    
def play_game(knowledge_split, ability_split, game, blocks):

    
    reprez = {}
    
    reprez['final_config'] = [{'id': b.id, 'bin': b.bin} for b in blocks] 
    reprez['start_config'] = {
        'player1' : [b.id for b,k in zip(blocks,ability_split) if not k],
        'player2' : [b.id for b,k in zip(blocks,ability_split) if k]
        
    }
    reprez['knowledge'] = {
        'player1' : [g for g,k in zip(game,knowledge_split) if k <= 1],
        'player2' : [g for g,k in zip(game,knowledge_split) if k >= 1]
    }
    
    return json.dumps(reprez,indent=2)

blocks = [Block(i,i%4) for i in range(8)]

games = game_maker([], blocks)
shuffle(games)



ability_splits = list(set(list(permutations([0]*(len(blocks)//2)+[1]*(len(blocks) - len(blocks)//2))) + (len(blocks)%2)*list(permutations([1]*(len(blocks)//2)+[0]*(len(blocks) - len(blocks)//2)))))
game  = choice(games)

knowledge_splits = list(set(sum([list(set(permutations([1]+[0]*a+[2]*b+[1]*(len(game)-a-b-1)))) for a in range(1,len(game)-3) for b in range(a,len(game)-a-2)],[])))

ability_splits = list(set(list(permutations([0]*(len(blocks)//2)+[1]*(len(blocks) - len(blocks)//2))) + (len(blocks)%2)*list(permutations([1]*(len(blocks)//2)+[0]*(len(blocks) - len(blocks)//2)))))

print(play_game(choice(knowledge_splits), choice(ability_splits), game, blocks))
