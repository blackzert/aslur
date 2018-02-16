struct gap_info {
	unsigned long gap_len;
	unsigned long gap_start;
	unsigned long gap_end;
	struct vm_area_struct *vma_next;
	struct vm_area_struct *vma_prev;
};



struct mm_struct {
	struct gap_info *gaps; 				/* list of free gaps */
	unsigned long gaps_count;
	struct vm_area_struct *mmap;		/* list of VMAs */
	struct rb_root mm_rb;

	....

};

struct vm_unmapped_area_info {
	unsigned long flags;
	unsigned long length;
	unsigned long low_limit;
	unsigned long high_limit;
	unsigned long align_mask;
	unsigned long align_offset;
};






unsigned long random_unmapped_area(struct vm_unmapped_area_info *info)
{
	struct mm_struct *mm = current->mm;
	struct gap_info *gaps = mm->gaps;
	struct vm_area_struct *vma;
	unsigned long length = info->length;
	unsigned long gap_idx;
	unsigned long hi = length - 1; 
	unsigned long low = 0;
	unsigned long choise;

	if (gaps[0] < length) 
		return -ENOMEM;

	if (gaps[hi] > length) {
		gap_idx = hi;
	}
	else {
		/* Search gap for logariphm */
		while(low<hi-1) {
			gap_idx = (hi + low) >> 1;
			if (length > gaps[gap_idx].gap_len)
				hi = gap_idx;
			else
				low = gap_idx;
		}
	}

	/* 
	gap_idx + 1 possible options
	cases:
		1. none of them out of range info->low..info->hi
			- choise random and return
		2. some of them out of range info->low.. info->hi
			- ususally only 2 gaps may be out of range - from PAGE_SIZE to first allocated page in memory, wause caused by mmap_min_address.
			Another one is from the top, with info->hi
			we just choise random here and try to find first suitable from here. Will check 3 times to get result
			- If mmap_min_address changed we need up to gap_idx + 1 tries to find gap.
		3. all of them out of range info->low..info->hi
			- cover by previous case I think.
	*/
	gap_idx++;
	last_choise = choise = get_random_long() % gap_idx;
	found = 0;
	do {
		if (gaps[choise].gap_start > info->low_limit  && gaps[choise].gap_end < info->high_limit){
			found = 1;
			break;
		}
		choise = (choise + 1) % gap_idx;
	}while(last_choise != choise);
	
	
	if (!found) 
		return -ENOMEM;
	tmp = (gaps[choise].gap_end - gaps[choise].gap_start) >> PAGE_SHIFT
	if (tmp == 0)
		return gap.start;

	tmp = get_random_long() % tmp;
	return gaps[choise].gap_start + (tmp << PAGE_SHIFT);
}